// EJ 22 — Decodificación de la salida del detector + NMS por clase — solución de referencia
// Compilar:  make sol22
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
using namespace std;
using namespace cv;

struct Detection {
    Rect box;
    int classId;
    float score;
};

// ---------------------------------------------------------------------------
// Tres fases: filtrar por confianza, agrupar por clase, NMS dentro de cada grupo.
//
// El filtro de confianza va PRIMERO por rendimiento: una salida de YOLO tiene
// 25.200 filas y típicamente sobreviven 20. Todo lo que hagas después opera
// sobre esas 20. En la Jetson esto importa: el post-proceso en CPU puede
// costar más que la inferencia en GPU si lo escribes al revés.
//
// max_element sobre el puntero crudo de la fila evita copiar los scores de
// clase a un vector intermedio.
// ---------------------------------------------------------------------------
vector<Detection> decodeDetections(const Mat& out, int numClasses,
                                   float confThr, float nmsThr) {
    if (out.empty()) return {};
    CV_Assert(out.type() == CV_32F && out.cols == 5 + numClasses);

    vector<Rect>  boxes;
    vector<float> scores;
    vector<int>   classIds;
    boxes.reserve(out.rows);

    for (int i = 0; i < out.rows; ++i) {
        const float* p = out.ptr<float>(i);
        const float* cls = p + 5;
        int best = static_cast<int>(max_element(cls, cls + numClasses) - cls);
        float score = p[4] * cls[best];              // objectness * score de clase
        if (score < confThr) continue;

        float cx = p[0], cy = p[1], w = p[2], h = p[3];
        boxes.emplace_back(cvRound(cx - w / 2), cvRound(cy - h / 2), cvRound(w), cvRound(h));
        scores.push_back(score);
        classIds.push_back(best);
    }

    // NMS POR CLASE: dnn::NMSBoxes no mira las clases, así que si le pasas todo
    // junto suprime una moto porque solapa con la persona que la conduce.
    map<int, vector<int>> byClass;                   // clase -> índices
    for (size_t i = 0; i < classIds.size(); ++i)
        byClass[classIds[i]].push_back(static_cast<int>(i));

    vector<Detection> res;
    for (const auto& [cls, idx] : byClass) {
        vector<Rect>  b; vector<float> s;
        b.reserve(idx.size()); s.reserve(idx.size());
        for (int i : idx) { b.push_back(boxes[i]); s.push_back(scores[i]); }

        vector<int> keep;
        dnn::NMSBoxes(b, s, confThr, nmsThr, keep);
        for (int k : keep) res.push_back({b[k], cls, s[k]});
    }

    sort(res.begin(), res.end(), [](const Detection& a, const Detection& b) {
        if (a.score != b.score) return a.score > b.score;
        return a.classId < b.classId;
    });
    return res;
}

// ===========================================================================
//                               TEST HARNESS
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

static void addRow(Mat& m, float cx, float cy, float w, float h, float obj,
                   const vector<float>& cls) {
    vector<float> row = {cx, cy, w, h, obj};
    row.insert(row.end(), cls.begin(), cls.end());
    m.push_back(Mat(1, (int)row.size(), CV_32F, row.data()).clone());
}

int main() {
    const int C = 3;
    Mat out(0, 5 + C, CV_32F);
    addRow(out,  50,  50,  20,  20, 0.90f, {0.80f, 0.10f, 0.10f});
    addRow(out,  52,  50,  20,  20, 0.70f, {0.90f, 0.05f, 0.05f});
    addRow(out, 200, 200,  30,  30, 0.20f, {0.50f, 0.30f, 0.20f});
    addRow(out,  51,  50,  20,  20, 0.85f, {0.05f, 0.90f, 0.05f});
    addRow(out, 300, 300,  40,  40, 0.95f, {0.10f, 0.10f, 0.90f});

    vector<Detection> d = decodeDetections(out, C, 0.25f, 0.45f);

    check(d.size() == 3, "22 quedan 3 detecciones (obtenidas " + to_string(d.size()) + ")");
    check(d[0].classId == 2 && abs(d[0].score - 0.855f) < 1e-4f, "22 ordenadas por score descendente");
    check(d[1].classId == 1 && abs(d[1].score - 0.765f) < 1e-4f, "22 el solape de OTRA clase sobrevive (NMS por clase)");
    check(d[2].classId == 0 && abs(d[2].score - 0.720f) < 1e-4f, "22 de las dos de la clase 0 gana la de mayor score");
    check(d[2].box == Rect(40, 40, 20, 20), "22 conversión centro+tamaño -> Rect(x,y,w,h)");
    check(d[0].box == Rect(280, 280, 40, 40), "22 caja lejana intacta");

    {
        check(decodeDetections(out, C, 0.9f, 0.45f).empty(), "22 confThr alto -> sin detecciones");
        vector<Detection> all = decodeDetections(out, C, 0.05f, 0.45f);
        check(all.size() == 4, "22 confThr bajo deja pasar la fila débil (obtenidas " +
                               to_string(all.size()) + ")");
        check(decodeDetections(out, C, 0.25f, 1.0f).size() == 4, "22 nmsThr=1.0 no suprime nada");
    }
    {
        check(decodeDetections(Mat(0, 5 + C, CV_32F), C, 0.25f, 0.45f).empty(),
              "22 tensor vacío -> sin detecciones");
        Mat one(0, 5 + C, CV_32F);
        addRow(one, 10, 10, 4, 4, 1.0f, {0.0f, 0.0f, 1.0f});
        vector<Detection> r = decodeDetections(one, C, 0.5f, 0.45f);
        check(r.size() == 1 && r[0].classId == 2 && r[0].box == Rect(8, 8, 4, 4),
              "22 una sola fila se decodifica bien");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

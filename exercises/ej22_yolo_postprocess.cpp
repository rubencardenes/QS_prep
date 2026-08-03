// EJ 22 — Post-proceso de un detector: decodificar el tensor de salida + NMS
//
// CÓMO USARLO
//   1. Rellena la función marcada con  // TODO.
//   2. Compila y ejecuta:   make ej22
//   3. Cronométrate: apunta a ~25 min.
//
// CONTEXTO TIPO ENTREVISTA
//   "Ya tienes la red corriendo en la Jetson. Su salida es un tensor de N filas
//    con [cx, cy, w, h, objectness, score_clase_0..C-1] en coordenadas de la
//    entrada de la red. Conviértelo en la lista final de detecciones."
//
//   Es el complemento exacto del EJ 17: aquel era el pre-proceso, este es el
//   post-proceso. Entre los dos tienes el pipeline completo de inferencia, que
//   es lo que de verdad se escribe en un puesto así.
//
// ESPECIFICACIÓN
//   - score de la fila = objectness * max(scores de clase);  classId = argmax.
//   - Descarta las filas con score < confThr.
//   - Caja: de centro+tamaño a esquina+tamaño -> Rect(cx-w/2, cy-h/2, w, h),
//     redondeando al entero más cercano.
//   - NMS **por clase** (dos objetos de clases distintas pueden solaparse:
//     una persona encima de una moto no debe eliminarse).
//   - Devuelve las detecciones ordenadas por score descendente (desempate:
//     classId ascendente).
//
// GOTCHAS
//   - cv::dnn::NMSBoxes es CLASS-AGNOSTIC: si le pasas todas las cajas juntas
//     te suprime detecciones válidas de clases distintas. Hay que agrupar por
//     clase (o usar el truco de desplazar las cajas por clase).
//   - El tensor real de YOLOv5 llega como 1 x N x (5+C): hay que "aplanarlo" a
//     N x (5+C) antes de recorrerlo. Aquí ya te lo damos en 2D para centrarnos
//     en el algoritmo.
//   - YOLOv8 NO tiene objectness: son 4 + C columnas y el score es directamente
//     el de clase. Preguntar por la versión del modelo es la respuesta correcta.
//   - Las coordenadas están en el espacio de la ENTRADA de la red (letterboxed);
//     para dibujarlas sobre el frame original hay que deshacer el letterbox
//     (EJ 17.c). No lo mezcles: primero NMS, luego el mapeo.

#include <algorithm>
#include <iostream>
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

// ===========================================================================
// 22 — decodeDetections
//   out: CV_32F de N filas x (5 + numClasses) columnas.
// ---------------------------------------------------------------------------
vector<Detection> decodeDetections(const Mat& out, int numClasses,
                                   float confThr, float nmsThr) {
    // TODO
    return {};
}

// ===========================================================================
//                        TEST HARNESS (no tocar)
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

// Construye una fila del tensor: cx, cy, w, h, obj, clases...
static void addRow(Mat& m, float cx, float cy, float w, float h, float obj,
                   const vector<float>& cls) {
    vector<float> row = {cx, cy, w, h, obj};
    row.insert(row.end(), cls.begin(), cls.end());
    m.push_back(Mat(1, (int)row.size(), CV_32F, row.data()).clone());
}

int main() {
    const int C = 3;
    Mat out(0, 5 + C, CV_32F);
    //      cx    cy    w     h     obj   scores por clase        -> score / clase
    addRow(out,  50,  50,  20,  20, 0.90f, {0.80f, 0.10f, 0.10f});  // 0.720  clase 0
    addRow(out,  52,  50,  20,  20, 0.70f, {0.90f, 0.05f, 0.05f});  // 0.630  clase 0  (solapa con la anterior)
    addRow(out, 200, 200,  30,  30, 0.20f, {0.50f, 0.30f, 0.20f});  // 0.100  bajo umbral
    addRow(out,  51,  50,  20,  20, 0.85f, {0.05f, 0.90f, 0.05f});  // 0.765  clase 1  (solapa, otra clase)
    addRow(out, 300, 300,  40,  40, 0.95f, {0.10f, 0.10f, 0.90f});  // 0.855  clase 2

    vector<Detection> d = decodeDetections(out, C, 0.25f, 0.45f);

    check(d.size() == 3, "22 quedan 3 detecciones (obtenidas " + to_string(d.size()) + ")");
    if (d.size() == 3) {
        check(d[0].classId == 2 && abs(d[0].score - 0.855f) < 1e-4f, "22 ordenadas por score descendente");
        check(d[1].classId == 1 && abs(d[1].score - 0.765f) < 1e-4f, "22 el solape de OTRA clase sobrevive (NMS por clase)");
        check(d[2].classId == 0 && abs(d[2].score - 0.720f) < 1e-4f, "22 de las dos de la clase 0 gana la de mayor score");
        check(d[2].box == Rect(40, 40, 20, 20), "22 conversión centro+tamaño -> Rect(x,y,w,h)");
        check(d[0].box == Rect(280, 280, 40, 40), "22 caja lejana intacta");
    }

    // --- umbrales -----------------------------------------------------------
    {
        check(decodeDetections(out, C, 0.9f, 0.45f).empty(), "22 confThr alto -> sin detecciones");
        vector<Detection> all = decodeDetections(out, C, 0.05f, 0.45f);
        check(all.size() == 4, "22 confThr bajo deja pasar la fila débil (obtenidas " +
                               to_string(all.size()) + ")");
        // nmsThr = 1.0 no suprime nada: ni siquiera cajas idénticas
        check(decodeDetections(out, C, 0.25f, 1.0f).size() == 4, "22 nmsThr=1.0 no suprime nada");
    }

    // --- degenerados ---------------------------------------------------------
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

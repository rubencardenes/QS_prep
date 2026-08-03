// EJ 17 — Letterbox, blob NCHW y mapeo de cajas — solución de referencia
// Compilar:  make sol17
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
using namespace std;
using namespace cv;

// ---------------------------------------------------------------------------
// 17.a — Letterbox: una sola escala (la menor) para no deformar, y el resto se
//   rellena. copyMakeBorder añade el marco de una vez; el reparto impar del
//   padding se resuelve dando el píxel sobrante al lado derecho/inferior.
//   INTER_AREA es la interpolación correcta al REDUCIR (promedia el área del
//   píxel origen, evita aliasing); INTER_LINEAR al ampliar.
// ---------------------------------------------------------------------------
Mat letterbox(const Mat& src, Size target, double& scale, int& padLeft, int& padTop,
              int padValue = 114) {
    scale = min(target.width / static_cast<double>(src.cols),
                target.height / static_cast<double>(src.rows));
    int newW = static_cast<int>(lround(src.cols * scale));
    int newH = static_cast<int>(lround(src.rows * scale));

    Mat resized;
    resize(src, resized, Size(newW, newH), 0, 0, scale < 1.0 ? INTER_AREA : INTER_LINEAR);

    padLeft = (target.width - newW) / 2;
    padTop  = (target.height - newH) / 2;
    int padRight  = target.width - newW - padLeft;
    int padBottom = target.height - newH - padTop;

    Mat out;
    copyMakeBorder(resized, out, padTop, padBottom, padLeft, padRight,
                   BORDER_CONSTANT, Scalar::all(padValue));
    return out;
}

// ---------------------------------------------------------------------------
// 17.b — HWC entrelazado (memoria de OpenCV) -> NCHW planar (lo que espera la red).
//   Índice destino: c*H*W + y*W + x.  Es exactamente lo que hace blobFromImage.
//   Ojo al orden de canales: OpenCV da BGR, la mayoría de modelos quieren RGB.
//   En producción esto se hace en GPU (cv::cuda o el preproceso de TensorRT):
//   este bucle en CPU es un cuello de botella típico en Jetson.
// ---------------------------------------------------------------------------
vector<float> toBlobNCHW(const Mat& bgr, bool swapRB, float alpha) {
    CV_Assert(bgr.type() == CV_8UC3);
    const int H = bgr.rows, W = bgr.cols, plane = H * W;
    vector<float> blob(3 * plane);

    for (int y = 0; y < H; ++y) {
        const Vec3b* row = bgr.ptr<Vec3b>(y);
        for (int x = 0; x < W; ++x) {
            for (int c = 0; c < 3; ++c) {
                int srcC = swapRB ? 2 - c : c;      // c=0 -> R si swapRB
                blob[c * plane + y * W + x] = row[x][srcC] * alpha;
            }
        }
    }
    return blob;
}

// ---------------------------------------------------------------------------
// 17.c — Deshacer el letterbox: primero quitar el padding, después dividir por
//   la escala (en ese orden; al revés sale mal). El & con el rect de la imagen
//   recorta la caja a los límites válidos.
//   Fallar aquí es el bug clásico de "las cajas salen desplazadas".
// ---------------------------------------------------------------------------
Rect mapBoxBack(const Rect& box, double scale, int padLeft, int padTop, Size origSize) {
    double x0 = (box.x - padLeft) / scale;
    double y0 = (box.y - padTop) / scale;
    double x1 = (box.x + box.width  - padLeft) / scale;
    double y1 = (box.y + box.height - padTop) / scale;

    Rect r(static_cast<int>(lround(x0)), static_cast<int>(lround(y0)),
           static_cast<int>(lround(x1 - x0)), static_cast<int>(lround(y1 - y0)));
    return r & Rect(0, 0, origSize.width, origSize.height);
}

// ===========================================================================
//                               TEST HARNESS
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

int main() {
    {
        Mat src(50, 100, CV_8UC3, Scalar(0, 0, 255));
        double s = 0; int pl = 0, pt = 0;
        Mat out = letterbox(src, Size(64, 64), s, pl, pt);

        check(out.size() == Size(64, 64) && out.type() == CV_8UC3, "17.a salida 64x64 CV_8UC3");
        check(abs(s - 0.64) < 1e-9, "17.a escala = min(64/100, 64/50) = 0.64");
        check(pl == 0 && pt == 16, "17.a padding centrado: 0 izq, 16 arriba");
        check(out.at<Vec3b>(2, 32) == Vec3b(114, 114, 114), "17.a la banda superior es padding");
        check(out.at<Vec3b>(32, 32) == Vec3b(0, 0, 255), "17.a el contenido está en el centro");

        Mat sq(20, 20, CV_8UC3, Scalar(10, 20, 30));
        Mat o2 = letterbox(sq, Size(40, 40), s, pl, pt);
        check(abs(s - 2.0) < 1e-9 && pl == 0 && pt == 0, "17.a cuadrada -> sin padding, escala 2");
    }
    {
        Mat img(2, 2, CV_8UC3);
        img.at<Vec3b>(0, 0) = Vec3b(1, 2, 3);      img.at<Vec3b>(0, 1) = Vec3b(4, 5, 6);
        img.at<Vec3b>(1, 0) = Vec3b(7, 8, 9);      img.at<Vec3b>(1, 1) = Vec3b(10, 11, 12);

        vector<float> b = toBlobNCHW(img, false, 1.0f);
        check(b.size() == 12, "17.b tamaño 3*H*W");
        check(b[0] == 1 && b[1] == 4 && b[2] == 7 && b[3] == 10 &&
              b[8] == 3 && b[9] == 6 && b[10] == 9 && b[11] == 12,
              "17.b layout NCHW: canal completo antes del siguiente");

        vector<float> r = toBlobNCHW(img, true, 1.0f);
        check(r[0] == 3 && r[8] == 1, "17.b swapRB pone R primero y B último");

        Mat rnd(8, 5, CV_8UC3);
        randu(rnd, Scalar::all(0), Scalar::all(256));
        vector<float> mine = toBlobNCHW(rnd, true, 1.0f / 255.0f);
        Mat ref = dnn::blobFromImage(rnd, 1.0 / 255.0, Size(), Scalar(), true, false, CV_32F);
        bool same = mine.size() == static_cast<size_t>(ref.total());
        for (size_t i = 0; same && i < mine.size(); ++i)
            same = fabs(mine[i] - ref.ptr<float>()[i]) < 1e-6f;
        check(same, "17.b coincide con cv::dnn::blobFromImage");
    }
    {
        Size orig(100, 50);
        double s = 0.64; int pl = 0, pt = 16;
        check(mapBoxBack(Rect(0, 16, 64, 32), s, pl, pt, orig) == Rect(0, 0, 100, 50),
              "17.c la caja que cubre el contenido -> imagen completa");
        check(mapBoxBack(Rect(0, 16, 32, 32), s, pl, pt, orig) == Rect(0, 0, 50, 50),
              "17.c mitad izquierda -> mitad de la original");
        check(mapBoxBack(Rect(0, 0, 64, 64), s, pl, pt, orig) == Rect(0, 0, 100, 50),
              "17.c recorta a los límites de la original");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

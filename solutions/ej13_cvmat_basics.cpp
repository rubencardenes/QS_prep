// EJ 13 — cv::Mat esenciales — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej13_cvmat_basics.cpp \
//                $(pkg-config --cflags --libs opencv4) -o sol13 && ./sol13
//            (o:  make sol13)
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace cv;

// ---------------------------------------------------------------------------
// 13.a — Recorrido eficiente por punteros de fila.
//   ptr<uchar>(y) evita el coste de at<>() y funciona aunque la Mat sea un ROI
//   (no continua): cada fila tiene su propio puntero, el `step` lo gestiona Mat.
//   Si quisieras un único bucle plano, primero comprueba isContinuous().
// ---------------------------------------------------------------------------
int countAbove(const Mat& gray, uchar thr) {
    CV_Assert(gray.type() == CV_8UC1);
    int n = 0;
    for (int y = 0; y < gray.rows; ++y) {
        const uchar* row = gray.ptr<uchar>(y);
        for (int x = 0; x < gray.cols; ++x)
            if (row[x] > thr) ++n;
    }
    return n;
}

// ---------------------------------------------------------------------------
// 13.b — BGR -> gris a mano. El orden del canal es B,G,R (gotcha clásico).
//   Acumula en float/int: sumar uchar directamente desbordaría.
//   saturate_cast<uchar> redondea y recorta a 0..255 en una sola operación.
// ---------------------------------------------------------------------------
Mat toGrayManual(const Mat& bgr) {
    CV_Assert(bgr.type() == CV_8UC3);
    Mat out(bgr.size(), CV_8UC1);
    for (int y = 0; y < bgr.rows; ++y) {
        const Vec3b* src = bgr.ptr<Vec3b>(y);
        uchar* dst = out.ptr<uchar>(y);
        for (int x = 0; x < bgr.cols; ++x) {
            float v = 0.114f * src[x][0] + 0.587f * src[x][1] + 0.299f * src[x][2];
            dst[x] = saturate_cast<uchar>(v);
        }
    }
    return out;
}

// ---------------------------------------------------------------------------
// 13.c — Un ROI es una VISTA: img(rect) comparte el buffer con img, así que
//   setTo() escribe en el original sin copiar nada. El & con Rect(0,0,w,h)
//   recorta la intersección (evita la excepción si el rect se sale).
// ---------------------------------------------------------------------------
void paintRoi(Mat& img, const Rect& roi, const Scalar& color) {
    Rect safe = roi & Rect(0, 0, img.cols, img.rows);
    if (safe.width <= 0 || safe.height <= 0) return;
    img(safe).setTo(color);
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
        uchar data[] = {  0,  50, 100, 150,
                        200, 255,  10, 100,
                        101,  99, 128, 255};
        Mat g(3, 4, CV_8UC1, data);   // Mat sobre buffer externo: NO copia

        check(countAbove(g, 100) == 6, "13.a cuenta píxeles > 100");
        check(countAbove(g, 255) == 0, "13.a ninguno > 255");
        check(countAbove(g(Rect(1, 0, 2, 3)), 90) == 4, "13.a funciona sobre un ROI no continuo");
    }
    {
        Mat bgr(5, 7, CV_8UC3);
        randu(bgr, Scalar::all(0), Scalar::all(256));
        Mat mine = toGrayManual(bgr), ref;
        cvtColor(bgr, ref, COLOR_BGR2GRAY);
        bool okType = !mine.empty() && mine.type() == CV_8UC1 && mine.size() == bgr.size();
        double maxDiff = okType ? norm(mine, ref, NORM_INF) : 1e9;
        check(okType, "13.b devuelve CV_8UC1 del mismo tamaño");
        check(maxDiff <= 1.0, "13.b coincide con cvtColor (BGR, no RGB)");

        Mat red(1, 1, CV_8UC3, Scalar(0, 0, 255));
        Mat y = toGrayManual(red);
        check(abs(int(y.at<uchar>(0, 0)) - 76) <= 1, "13.b rojo puro -> 76 (orden BGR)");
    }
    {
        Mat img(10, 10, CV_8UC1, Scalar(0));
        Mat vista = img;
        Mat copia = img.clone();
        paintRoi(img, Rect(2, 3, 4, 5), Scalar(255));
        check(img.at<uchar>(3, 2) == 255 && img.at<uchar>(7, 5) == 255, "13.c pinta dentro del ROI (y,x)");
        check(img.at<uchar>(2, 2) == 0 && img.at<uchar>(8, 5) == 0, "13.c no toca fuera del ROI");
        check(vista.at<uchar>(3, 2) == 255, "13.c Mat asignada comparte datos");
        check(copia.at<uchar>(3, 2) == 0, "13.c clone() es copia profunda");

        Mat small(4, 4, CV_8UC1, Scalar(0));
        paintRoi(small, Rect(2, 2, 10, 10), Scalar(255));
        check(small.at<uchar>(3, 3) == 255 && small.at<uchar>(1, 1) == 0, "13.c recorta el ROI fuera de rango");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

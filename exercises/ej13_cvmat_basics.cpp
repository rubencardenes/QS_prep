// EJ 13 — cv::Mat esenciales: acceso por punteros, BGR y vistas compartidas
//
// CÓMO USARLO
//   1. Rellena las funciones marcadas con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej13_cvmat_basics.cpp \
//            $(pkg-config --cflags --libs opencv4) -o ej13 && ./ej13
//      (o simplemente:  make ej13)
//   3. Cronométrate: apunta a ~15 min.
//   4. Solo si te atascas, mira solutions/ej13_cvmat_basics.cpp.
//
// GOTCHAS QUE SE EVALÚAN AQUÍ
//   - OpenCV almacena en BGR, no RGB.
//   - at<T>(y, x) es (fila, columna), NO (x, y).
//   - Mat copia por referencia: `Mat b = a;` comparte datos; usa clone() para copia profunda.
//   - Un ROI `img(rect)` es una VISTA sobre el original: escribir en él modifica img.
//   - Sumar uint8 desborda: acumula en int/float y usa saturate_cast al escribir.

#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace cv;

// ===========================================================================
// 13.a — countAbove
//   Devuelve cuántos píxeles de una imagen CV_8UC1 son ESTRICTAMENTE mayores
//   que thr. Recórrela con punteros de fila (ptr<uchar>(y)), no con at<>(),
//   y ten en cuenta que la Mat puede no ser continua (ROI): itera fila a fila.
// ---------------------------------------------------------------------------
int countAbove(const Mat& gray, uchar thr) {
    int n = 0;
    for (int y = 0;y < gray.rows.size();++y) {
        const uchar* row = gray.ptr<uchar>(y);
        for (int x= 0;x < gray.cols; ++x) {
            if (row[x] > thr) ++n;
        }
    }
    return n;
}

// ===========================================================================
// 13.b — toGrayManual
//   Convierte una CV_8UC3 (BGR) a CV_8UC1 a mano, con los pesos de luminancia
//   que usa OpenCV:   Y = 0.299*R + 0.587*G + 0.114*B
//   Redondea al entero más cercano. Debe coincidir con cvtColor(±1).
// ---------------------------------------------------------------------------
Mat toGrayManual(const Mat& bgr) {
    Mat grey(bgr.size, CV_8UC1);
    auto clamp = [](int v, int low, int high) { return min(max(v, low), high);};
    for (int y=0;y < bgr.rows; ++y) {
        const Vec3b* rows_in = bgr.ptr<Vec3b>(y);
        uchar* rows_out = grey.ptr<uchar>(y);
        for (int x = 0;x < bgr.cols; ++x) {
            float v = rows_in[x][2]*0.299 + rows_in[x][1]*0.587 + rows_in[x][0]*0.114;
            rows_out[x] = clamp(round(v), 0, 255);
        }
    }
    return grey;
}

// ===========================================================================
// 13.c — paintRoi
//   Pinta el rectángulo roi de img con color, SIN copiar la imagen entera y
//   sin recorrer píxel a píxel (usa la vista ROI + setTo).
//   Debe recortar roi a los límites de img: si se sale, no debe petar.
// ---------------------------------------------------------------------------
void paintRoi(Mat& img, const Rect& roi, const Scalar& color) {
    // TODO
}

// ===========================================================================
//                        TEST HARNESS (no tocar)
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

int main() {
    // --- 13.a ---------------------------------------------------------------
    {
        uchar data[] = {  0,  50, 100, 150,
                        200, 255,  10, 100,
                        101,  99, 128, 255};
        Mat g(3, 4, CV_8UC1, data);   // Mat sobre buffer externo: NO copia

        check(countAbove(g, 100) == 6, "13.a cuenta píxeles > 100");
        check(countAbove(g, 255) == 0, "13.a ninguno > 255");
        // ROI no continuo: columnas 1..2 de las 3 filas -> {50,100, 255,10, 99,128}
        check(countAbove(g(Rect(1, 0, 2, 3)), 90) == 4, "13.a funciona sobre un ROI no continuo");
    }

    // --- 13.b ---------------------------------------------------------------
    {
        Mat bgr(5, 7, CV_8UC3);
        randu(bgr, Scalar::all(0), Scalar::all(256));
        Mat mine = toGrayManual(bgr), ref;
        cvtColor(bgr, ref, COLOR_BGR2GRAY);
        bool okType = !mine.empty() && mine.type() == CV_8UC1 && mine.size() == bgr.size();
        double maxDiff = okType ? norm(mine, ref, NORM_INF) : 1e9;
        check(okType, "13.b devuelve CV_8UC1 del mismo tamaño");
        check(maxDiff <= 1.0, "13.b coincide con cvtColor (BGR, no RGB)");

        // Rojo puro en BGR = (0,0,255) -> Y ~ 76 ; si sale ~29 has confundido el orden
        Mat red(1, 1, CV_8UC3, Scalar(0, 0, 255));
        Mat y = toGrayManual(red);
        check(!y.empty() && abs(int(y.at<uchar>(0, 0)) - 76) <= 1, "13.b rojo puro -> 76 (orden BGR)");
    }

    // --- 13.c ---------------------------------------------------------------
    {
        Mat img(10, 10, CV_8UC1, Scalar(0));
        Mat vista = img;              // comparte datos
        Mat copia = img.clone();      // copia profunda
        paintRoi(img, Rect(2, 3, 4, 5), Scalar(255));
        check(img.at<uchar>(3, 2) == 255 && img.at<uchar>(7, 5) == 255, "13.c pinta dentro del ROI (y,x)");
        check(img.at<uchar>(2, 2) == 0 && img.at<uchar>(8, 5) == 0, "13.c no toca fuera del ROI");
        check(vista.at<uchar>(3, 2) == 255, "13.c Mat asignada comparte datos");
        check(copia.at<uchar>(3, 2) == 0, "13.c clone() es copia profunda");

        Mat small(4, 4, CV_8UC1, Scalar(0));
        paintRoi(small, Rect(2, 2, 10, 10), Scalar(255));   // se sale: hay que recortar
        check(small.at<uchar>(3, 3) == 255 && small.at<uchar>(1, 1) == 0, "13.c recorta el ROI fuera de rango");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

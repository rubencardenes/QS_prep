// EJ 14 — Segmentación por color (HSV) + Otsu + morfología — solución de referencia
// Compilar:  make sol14
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace cv;

// ---------------------------------------------------------------------------
// 14.a — El rojo está en los dos extremos del círculo de tono: en OpenCV
//   H ∈ [0,179], así que hacen falta dos inRange y un OR (bitwise_or).
//   S mínimo evita coger blancos/grises desaturados; V mínimo evita negros.
//   MORPH_OPEN = erosión seguida de dilatación: mata motas de 1-2 px y
//   devuelve el objeto grande a su tamaño original.
// ---------------------------------------------------------------------------
Mat segmentRed(const Mat& bgr) {
    CV_Assert(bgr.type() == CV_8UC3);
    Mat hsv;
    cvtColor(bgr, hsv, COLOR_BGR2HSV);

    Mat lo, hi, mask;
    inRange(hsv, Scalar(0,   80, 50), Scalar(10,  255, 255), lo);
    inRange(hsv, Scalar(170, 80, 50), Scalar(179, 255, 255), hi);
    bitwise_or(lo, hi, mask);

    Mat k = getStructuringElement(MORPH_RECT, Size(3, 3));
    morphologyEx(mask, mask, MORPH_OPEN, k);   // fuera motas
    return mask;
}

// ---------------------------------------------------------------------------
// 14.b — Otsu busca el umbral que minimiza la varianza intra-clase. Se pide
//   con la flag THRESH_OTSU; el valor que pases como umbral se ignora y
//   threshold() devuelve el umbral calculado.
//   Sólo vale para CV_8UC1 y funciona bien si el histograma es bimodal.
// ---------------------------------------------------------------------------
int otsuThreshold(const Mat& gray, Mat& mask) {
    CV_Assert(gray.type() == CV_8UC1);
    double t = threshold(gray, mask, 0, 255, THRESH_BINARY | THRESH_OTSU);
    return static_cast<int>(t);
}

// ===========================================================================
//                               TEST HARNESS
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

static Mat makeScene() {
    Mat img(60, 60, CV_8UC3, Scalar(0, 0, 0));
    rectangle(img, Rect(10, 10, 20, 20), Scalar(0, 0, 255), FILLED);
    rectangle(img, Rect(38, 38, 15, 15), Scalar(255, 0, 0), FILLED);
    img.at<Vec3b>(50, 5) = Vec3b(0, 0, 230);
    img.at<Vec3b>(3, 55) = Vec3b(0, 0, 200);
    return img;
}

int main() {
    {
        Mat scene = makeScene();
        Mat m = segmentRed(scene);
        bool okType = !m.empty() && m.type() == CV_8UC1 && m.size() == scene.size();
        check(okType, "14.a devuelve máscara CV_8UC1 del tamaño de la entrada");
        check(m.at<uchar>(15, 15) == 255 && m.at<uchar>(29, 29) == 255, "14.a detecta el cuadrado rojo");
        check(m.at<uchar>(45, 45) == 0, "14.a NO detecta el azul (BGR vs HSV bien hecho)");
        check(m.at<uchar>(50, 5) == 0 && m.at<uchar>(3, 55) == 0, "14.a la apertura elimina las motas de 1 px");
        int area = countNonZero(m);
        check(area >= 380 && area <= 400, "14.a área ≈ 400 px del cuadrado (obtenido: " + to_string(area) + ")");
    }
    {
        Mat img(20, 20, CV_8UC3, Scalar(0, 0, 0));
        rectangle(img, Rect(4, 4, 12, 12), Scalar(20, 0, 255), FILLED);
        Mat m = segmentRed(img);
        check(m.at<uchar>(10, 10) == 255, "14.a cubre también el tramo H≈170-179 del rojo");
    }
    {
        Mat gray(40, 40, CV_8UC1, Scalar(50));
        gray(Rect(0, 0, 40, 20)).setTo(200);
        Mat mask;
        int thr = otsuThreshold(gray, mask);
        check(thr >= 50 && thr < 200, "14.b Otsu elige un umbral entre las dos modas (obtenido: " + to_string(thr) + ")");
        check(mask.type() == CV_8UC1 && mask.at<uchar>(5, 5) == 255 && mask.at<uchar>(30, 5) == 0,
              "14.b máscara binaria correcta (claro=255, oscuro=0)");
        check(countNonZero(mask) == 800, "14.b cuenta exacta de píxeles claros");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

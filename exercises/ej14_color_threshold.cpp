// EJ 14 — Segmentación por color (HSV) + umbral Otsu + morfología
//
// CÓMO USARLO
//   1. Rellena las funciones marcadas con  // TODO.
//   2. Compila y ejecuta:   make ej14
//      (o: g++ -std=c++17 -O2 -Wall exercises/ej14_color_threshold.cpp \
//              $(pkg-config --cflags --libs opencv4) -o ej14 && ./ej14)
//   3. Cronométrate: apunta a ~15-20 min.
//
// CONTEXTO TIPO ENTREVISTA
//   "Tenemos un dron que debe localizar marcadores rojos en el suelo. Dame una
//    máscara binaria limpia del color rojo, robusta a ruido sal-y-pimienta."
//
// GOTCHAS
//   - En OpenCV, H va de 0 a 179 (no 0-360). El ROJO está partido en dos
//     tramos: H≈0-10 y H≈170-179 -> necesitas DOS inRange y un OR.
//   - Segmenta en HSV, no en BGR: separa color (H) de iluminación (V).
//   - MORPH_OPEN (erosión+dilatación) quita motas; MORPH_CLOSE tapa agujeros.

#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace cv;

// ===========================================================================
// 14.a — segmentRed
//   Entrada: imagen BGR (CV_8UC3). Salida: máscara CV_8UC1 con 0 / 255.
//   Pasos: cvtColor a HSV -> inRange en los dos tramos de rojo -> OR ->
//          MORPH_OPEN con kernel 3x3 para eliminar píxeles sueltos.
//   Usa saturación y valor mínimos (p.ej. S>=80, V>=50) para no coger grises.
// ---------------------------------------------------------------------------
Mat segmentRed(const Mat& bgr) {
    // TODO
    return Mat();
}

// ===========================================================================
// 14.b — otsuThreshold
//   Binariza gray con el método de Otsu (umbral automático) y escribe el
//   resultado en mask (0/255, blanco = por encima del umbral).
//   Devuelve el umbral que ha elegido Otsu.
// ---------------------------------------------------------------------------
int otsuThreshold(const Mat& gray, Mat& mask) {
    // TODO
    return -1;
}

// ===========================================================================
//                        TEST HARNESS (no tocar)
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

// Escena sintética: cuadrado rojo, cuadrado azul, y motas rojas de 1 píxel.
static Mat makeScene() {
    Mat img(60, 60, CV_8UC3, Scalar(0, 0, 0));
    rectangle(img, Rect(10, 10, 20, 20), Scalar(0, 0, 255), FILLED);   // rojo puro
    rectangle(img, Rect(38, 38, 15, 15), Scalar(255, 0, 0), FILLED);   // azul puro
    img.at<Vec3b>(50, 5) = Vec3b(0, 0, 230);                           // mota roja
    img.at<Vec3b>(3, 55) = Vec3b(0, 0, 200);                           // mota roja
    return img;
}

int main() {
    // --- 14.a ---------------------------------------------------------------
    {
        Mat scene = makeScene();
        Mat m = segmentRed(scene);
        bool okType = !m.empty() && m.type() == CV_8UC1 && m.size() == scene.size();
        check(okType, "14.a devuelve máscara CV_8UC1 del tamaño de la entrada");
        if (okType) {
            check(m.at<uchar>(15, 15) == 255 && m.at<uchar>(29, 29) == 255, "14.a detecta el cuadrado rojo");
            check(m.at<uchar>(45, 45) == 0, "14.a NO detecta el azul (BGR vs HSV bien hecho)");
            check(m.at<uchar>(50, 5) == 0 && m.at<uchar>(3, 55) == 0, "14.a la apertura elimina las motas de 1 px");
            int area = countNonZero(m);
            check(area >= 380 && area <= 400, "14.a área ≈ 400 px del cuadrado (obtenido: " + to_string(area) + ")");
        }
    }
    // Rojo en el tramo alto de H (H≈179): un rojo ligeramente "hacia magenta"
    {
        Mat img(20, 20, CV_8UC3, Scalar(0, 0, 0));
        rectangle(img, Rect(4, 4, 12, 12), Scalar(20, 0, 255), FILLED);  // H ≈ 178
        Mat m = segmentRed(img);
        check(!m.empty() && m.at<uchar>(10, 10) == 255, "14.a cubre también el tramo H≈170-179 del rojo");
    }

    // --- 14.b ---------------------------------------------------------------
    {
        Mat gray(40, 40, CV_8UC1, Scalar(50));
        gray(Rect(0, 0, 40, 20)).setTo(200);          // imagen bimodal 50/200
        Mat mask;
        int thr = otsuThreshold(gray, mask);
        check(thr >= 50 && thr < 200, "14.b Otsu elige un umbral entre las dos modas (obtenido: " + to_string(thr) + ")");
        bool okMask = !mask.empty() && mask.type() == CV_8UC1 &&
                      mask.at<uchar>(5, 5) == 255 && mask.at<uchar>(30, 5) == 0;
        check(okMask, "14.b máscara binaria correcta (claro=255, oscuro=0)");
        check(!mask.empty() && countNonZero(mask) == 800, "14.b cuenta exacta de píxeles claros");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

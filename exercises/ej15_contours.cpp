// EJ 15 — findContours: cajas de detección y forma del objeto
//
// CÓMO USARLO
//   1. Rellena las funciones marcadas con  // TODO.
//   2. Compila y ejecuta:   make ej15
//   3. Cronométrate: apunta a ~20 min.
//
// CONTEXTO TIPO ENTREVISTA
//   "De una máscara binaria (la del ejercicio anterior), sácame las bounding
//    boxes de los objetos, descartando el ruido pequeño, ordenadas de mayor a
//    menor. Y dime si el objeto principal es un cuadrilátero o un triángulo."
//
// GOTCHAS
//   - findContours espera CV_8UC1 binaria. En OpenCV 4 NO modifica la entrada.
//   - RETR_EXTERNAL = solo contornos externos (ignora agujeros interiores).
//   - contourArea() (área del polígono) != countNonZero() (píxeles): para un
//     cuadrado de 20x20 píxeles el contorno mide 19x19 = 361. No te sorprendas.
//   - boundingRect() sí devuelve el rectángulo exacto en píxeles (20x20).
//   - approxPolyDP con epsilon = ratio * arcLength() simplifica el polígono.

#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>
#if CV_VERSION_MAJOR >= 5
#include <opencv2/geometry.hpp>   // OpenCV 5 movió contourArea/boundingRect/arcLength aquí
#endif
using namespace std;
using namespace cv;

// ===========================================================================
// 15.a — detectBoxes
//   Entrada: máscara binaria (CV_8UC1, 0/255) y área mínima de contorno.
//   Salida: bounding boxes de los contornos EXTERNOS con contourArea >= minArea,
//           ordenadas por área de la caja de MAYOR a MENOR.
// ---------------------------------------------------------------------------
vector<Rect> detectBoxes(const Mat& mask, double minArea) {
    vector<vector<Point>> contours; 
    findContours(mask, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
    vector<Rect> bboxes;
    for (int i=0;i<contours.size();++i) {
        if (contourArea(contours[i]) > minArea)
           bboxes.push_back(boundingRect(contours[i]));  
    }
    sort(bboxes.begin(), bboxes.end(), [](Rect a, Rect b){return a.width*a.height > b.width*b.height;});

    return bboxes;
}

// ===========================================================================
// 15.b — countVertices
//   Devuelve el número de vértices del contorno externo MÁS GRANDE tras
//   simplificarlo con approxPolyDP (epsilon = epsRatio * perímetro).
//   Si no hay contornos, devuelve 0.
// ---------------------------------------------------------------------------
int countVertices(const Mat& mask, double epsRatio = 0.02) {
    vector<vector<Point>> contours; 
    findContours(mask, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
    if (contours.empty()) return 0;
    auto it = max_element(contours.begin(), contours.end(), 
                        [](vector<Point> a, vector<Point> b) {return contourArea(a) < contourArea(b);});
    vector<Point> approx;
    approxPolyDP(*it, approx, epsRatio * arcLength(*it, true), true);
    
    return approx.size();
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
    // --- 15.a ---------------------------------------------------------------
    {
        Mat mask(80, 120, CV_8UC1, Scalar(0));
        rectangle(mask, Rect(10, 10, 30, 30), Scalar(255), FILLED);   // grande
        rectangle(mask, Rect(60, 10, 20, 20), Scalar(255), FILLED);   // mediano
        rectangle(mask, Rect(90, 50, 12, 12), Scalar(255), FILLED);   // pequeño
        rectangle(mask, Rect(5, 70, 2, 2),   Scalar(255), FILLED);    // ruido

        vector<Rect> boxes = detectBoxes(mask, 20.0);
        check(boxes.size() == 3, "15.a descarta el ruido (esperadas 3 cajas, obtenidas " +
                                 to_string(boxes.size()) + ")");
        if (boxes.size() == 3) {
            check(boxes[0] == Rect(10, 10, 30, 30), "15.a la primera caja es la mayor y exacta");
            check(boxes[1] == Rect(60, 10, 20, 20), "15.a segunda caja correcta");
            check(boxes[2] == Rect(90, 50, 12, 12), "15.a tercera caja correcta");
        }

        vector<Rect> todas = detectBoxes(mask, 0.0);
        check(todas.size() == 4, "15.a con minArea=0 salen las 4");
        check(detectBoxes(Mat(20, 20, CV_8UC1, Scalar(0)), 0.0).empty(), "15.a máscara vacía -> sin cajas");
    }

    // --- 15.b ---------------------------------------------------------------
    {
        Mat sq(60, 60, CV_8UC1, Scalar(0));
        rectangle(sq, Rect(10, 10, 40, 30), Scalar(255), FILLED);
        check(countVertices(sq) == 4, "15.b un rectángulo tiene 4 vértices");

        Mat tri(80, 80, CV_8UC1, Scalar(0));
        vector<Point> pts = {Point(40, 10), Point(70, 65), Point(10, 65)};
        fillConvexPoly(tri, pts, Scalar(255));
        check(countVertices(tri) == 3, "15.b un triángulo tiene 3 vértices");

        check(countVertices(Mat(10, 10, CV_8UC1, Scalar(0))) == 0, "15.b sin contornos -> 0");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

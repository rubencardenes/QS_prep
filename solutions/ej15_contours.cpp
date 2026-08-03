// EJ 15 — findContours: cajas de detección y forma — solución de referencia
// Compilar:  make sol15
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

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

// ---------------------------------------------------------------------------
// 15.a — RETR_EXTERNAL ignora contornos hijos (agujeros); CHAIN_APPROX_SIMPLE
//   comprime los tramos rectos (4 puntos para un rectángulo en vez de todo el
//   borde) -> menos memoria y más rápido.
//   Filtramos por contourArea (área del polígono) y ordenamos por área de la
//   caja con un lambda; sort no es estable, usa stable_sort si el orden entre
//   empates importa.
// ---------------------------------------------------------------------------
vector<Rect> detectBoxes(const Mat& mask, double minArea) {
    CV_Assert(mask.type() == CV_8UC1);
    vector<vector<Point>> contours;
    findContours(mask, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);

    vector<Rect> boxes;
    boxes.reserve(contours.size());
    for (const auto& c : contours)
        if (contourArea(c) >= minArea)
            boxes.push_back(boundingRect(c));

    sort(boxes.begin(), boxes.end(),
         [](const Rect& a, const Rect& b) { return a.area() > b.area(); });
    return boxes;
}

// ---------------------------------------------------------------------------
// 15.b — El contorno mayor se elige por contourArea (no por número de puntos).
//   approxPolyDP (Ramer-Douglas-Peucker) simplifica el polígono con una
//   tolerancia proporcional al perímetro: así el epsilon escala con el tamaño
//   del objeto y el criterio vale igual para un objeto cerca o lejos.
//   Con esto se clasifican formas: 3 = triángulo, 4 = cuadrilátero, >6 ≈ círculo.
// ---------------------------------------------------------------------------
int countVertices(const Mat& mask, double epsRatio = 0.02) {
    vector<vector<Point>> contours;
    findContours(mask, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
    if (contours.empty()) return 0;

    auto it = max_element(contours.begin(), contours.end(),
                          [](const vector<Point>& a, const vector<Point>& b) {
                              return contourArea(a) < contourArea(b);
                          });
    vector<Point> approx;
    approxPolyDP(*it, approx, epsRatio * arcLength(*it, true), true);
    return static_cast<int>(approx.size());
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
        Mat mask(80, 120, CV_8UC1, Scalar(0));
        rectangle(mask, Rect(10, 10, 30, 30), Scalar(255), FILLED);
        rectangle(mask, Rect(60, 10, 20, 20), Scalar(255), FILLED);
        rectangle(mask, Rect(90, 50, 12, 12), Scalar(255), FILLED);
        rectangle(mask, Rect(5, 70, 2, 2),   Scalar(255), FILLED);

        vector<Rect> boxes = detectBoxes(mask, 20.0);
        check(boxes.size() == 3, "15.a descarta el ruido (esperadas 3 cajas, obtenidas " +
                                 to_string(boxes.size()) + ")");
        check(boxes[0] == Rect(10, 10, 30, 30), "15.a la primera caja es la mayor y exacta");
        check(boxes[1] == Rect(60, 10, 20, 20), "15.a segunda caja correcta");
        check(boxes[2] == Rect(90, 50, 12, 12), "15.a tercera caja correcta");

        check(detectBoxes(mask, 0.0).size() == 4, "15.a con minArea=0 salen las 4");
        check(detectBoxes(Mat(20, 20, CV_8UC1, Scalar(0)), 0.0).empty(), "15.a máscara vacía -> sin cajas");
    }
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

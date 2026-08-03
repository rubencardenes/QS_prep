// EJ 16 — Transformaciones geométricas: warpAffine y warpPerspective
//
// CÓMO USARLO
//   1. Rellena las funciones marcadas con  // TODO.
//   2. Compila y ejecuta:   make ej16
//   3. Cronométrate: apunta a ~20 min.
//
// CONTEXTO TIPO ENTREVISTA
//   "El gimbal nos da la imagen rotada: estabilízala. Y de un marcador
//    detectado en perspectiva (4 esquinas), sácame la vista rectificada."
//
// GOTCHAS
//   - getRotationMatrix2D devuelve una matriz 2x3 (afín); getPerspectiveTransform
//     una 3x3 (homografía). warpAffine <-> 2x3, warpPerspective <-> 3x3.
//   - El ángulo positivo es ANTIHORARIO y el centro es (x, y), no (fila, col).
//   - warp hace mapeo INVERSO (para cada píxel destino busca el origen), por eso
//     se le pasa la transformación directa y no hay agujeros en la salida.
//   - Interpolación: INTER_NEAREST (rápida, dentada) vs INTER_LINEAR (por defecto).
//   - getPerspectiveTransform necesita EXACTAMENTE 4 puntos y en el mismo orden
//     en origen y destino (si los cruzas, la imagen sale espejada/retorcida).

#include <iostream>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>
#if CV_VERSION_MAJOR >= 5
#include <opencv2/geometry.hpp>   // OpenCV 5 movió get*Transform / getRotationMatrix2D aquí
#endif
using namespace std;
using namespace cv;

// ===========================================================================
// 16.a — rotateAround
//   Rota src angleDeg grados (antihorario) alrededor de center, con escala
//   `scale`, manteniendo el MISMO tamaño de salida. Lo que quede fuera se
//   rellena con 0 (borde constante negro).
// ---------------------------------------------------------------------------
Mat rotateAround(const Mat& src, Point2f center, double angleDeg, double scale = 1.0) {
    // TODO
    Mat dest;
    //double angleRad = angleDeg * CV_PI / 180;
    //double cx = (1 -cos(angleRad))*center.x - sin(angleRad)*center.y;
    //double cy = sin(angleRad)*center.x + (1-cos(angleRad))*center.y;
    //Mat M = (Mat_<double>(2,3) << cos(angleRad), sin(angleRad), cx, -sin(angleRad), cos(angleRad), cy);
    Mat M = getRotationMatrix2D(center, angleDeg, scale);
    warpAffine(src, dest, M, src.size(), INTER_LINEAR, BORDER_CONSTANT, Scalar::all(0));

    return dest;
}

// ===========================================================================
// 16.b — rectify
//   quad son 4 puntos del original en orden [sup-izq, sup-der, inf-der, inf-izq].
//   Devuelve una imagen outW x outH con ese cuadrilátero "desenrollado" a un
//   rectángulo completo (homografía + warpPerspective).
// ---------------------------------------------------------------------------
Mat rectify(const Mat& src, const vector<Point2f>& quad, int outW, int outH) {
    vector<Point2f> ptsOut;
    ptsOut.push_back(Point2f(0.f,0.f));
    ptsOut.push_back(Point2f(outW-1.f,0.f));
    ptsOut.push_back(Point2f(outW-1.f,outH-1.f));
    ptsOut.push_back(Point2f(0.f,outH-1.f));
    Mat dst;
    Mat H = getPerspectiveTransform(quad, ptsOut);                 // apply H to POINTS, not pixels
    warpPerspective(src, dst, H, Size(outW,outH));

    return dst;
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
    // --- 16.a ---------------------------------------------------------------
    {
        // Marca blanca en la esquina superior izquierda de una imagen 100x100.
        Mat src(100, 100, CV_8UC1, Scalar(0));
        rectangle(src, Rect(5, 5, 10, 10), Scalar(255), FILLED);
        Point2f c(src.cols / 2.0f - 0.5f, src.rows / 2.0f - 0.5f);

        Mat r90 = rotateAround(src, c, 90.0);
        bool okType = !r90.empty() && r90.size() == src.size() && r90.type() == CV_8UC1;
        check(okType, "16.a mantiene tamaño y tipo");
        // 90° antihorario: (x,y)=(10,10) -> (x',y') = (cx+(y-cy), cy-(x-cx)) = (10, 89)
        check(okType && r90.at<uchar>(89, 10) == 255, "16.a 90° antihorario lleva la marca abajo-izquierda");
        check(okType && r90.at<uchar>(10, 10) == 0, "16.a la posición original queda vacía");

        // 4 rotaciones de 90° ≈ la imagen original
        Mat acc = src.clone();
        for (int i = 0; i < 4; ++i) acc = rotateAround(acc, c, 90.0);
        check(!acc.empty() && norm(acc, src, NORM_INF) <= 1.0, "16.a 4x90° vuelve al origen");

        // scale = 0.5 -> la marca se acerca al centro y el área blanca baja
        Mat half = rotateAround(src, c, 0.0, 0.5);
        check(!half.empty() && countNonZero(half) < countNonZero(src), "16.a scale<1 reduce el objeto");
    }

    // --- 16.b ---------------------------------------------------------------
    {
        // Cuadrilátero en perspectiva, relleno de blanco sobre fondo negro.
        Mat src(200, 200, CV_8UC1, Scalar(0));
        vector<Point> poly = {Point(40, 30), Point(160, 60), Point(150, 170), Point(30, 130)};
        fillConvexPoly(src, poly, Scalar(255));

        vector<Point2f> quad = {Point2f(40, 30), Point2f(160, 60), Point2f(150, 170), Point2f(30, 130)};
        Mat out = rectify(src, quad, 50, 50);
        bool okType = !out.empty() && out.size() == Size(50, 50) && out.type() == CV_8UC1;
        check(okType, "16.b devuelve una imagen 50x50 del mismo tipo");
        check(okType && out.at<uchar>(25, 25) == 255, "16.b el centro queda dentro del marcador");
        check(okType && mean(out)[0] > 235.0, "16.b casi todo el resultado es el marcador rectificado");
    }
    {
        // Identidad: rectificar la imagen entera debe devolver (casi) la misma imagen.
        Mat src(64, 64, CV_8UC1);
        randu(src, Scalar::all(0), Scalar::all(256));
        vector<Point2f> full = {Point2f(0, 0), Point2f(63, 0), Point2f(63, 63), Point2f(0, 63)};
        Mat out = rectify(src, full, 64, 64);
        check(!out.empty() && norm(out, src, NORM_INF) <= 1.0, "16.b esquinas completas -> transformación identidad");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

// EJ 16 — warpAffine / warpPerspective — solución de referencia
// Compilar:  make sol16
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <iostream>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>
#if CV_VERSION_MAJOR >= 5
#include <opencv2/geometry.hpp>   // OpenCV 5 movió get*Transform / getRotationMatrix2D aquí
#endif
using namespace std;
using namespace cv;

// ---------------------------------------------------------------------------
// 16.a — getRotationMatrix2D(center, angle, scale) construye la 2x3:
//     [ a  b  (1-a)*cx - b*cy ]      a = scale*cos(angle)
//     [-b  a   b*cx + (1-a)*cy]      b = scale*sin(angle)
//   El ángulo es antihorario y el centro va en coordenadas (x, y).
//   warpAffine hace mapeo inverso: para cada píxel de destino calcula de dónde
//   viene en origen e interpola -> salida sin agujeros.
//   BORDER_CONSTANT + valor 0 rellena de negro lo que entra desde fuera.
// ---------------------------------------------------------------------------
Mat rotateAround(const Mat& src, Point2f center, double angleDeg, double scale = 1.0) {
    Mat M = getRotationMatrix2D(center, angleDeg, scale);
    Mat dst;
    warpAffine(src, dst, M, src.size(), INTER_LINEAR, BORDER_CONSTANT, Scalar::all(0));
    return dst;
}

// ---------------------------------------------------------------------------
// 16.b — Homografía: 8 grados de libertad -> 4 correspondencias de puntos
//   exactas. getPerspectiveTransform devuelve la 3x3 y warpPerspective la aplica.
//   El destino es el rectángulo completo de salida; el orden de los 4 puntos
//   debe corresponderse uno a uno con el de quad (aquí: TL, TR, BR, BL).
//   Nota: usar (outW-1, outH-1) mapea las esquinas a los píxeles extremos, que
//   es lo que hace que el caso "esquinas completas" salga identidad exacta.
// ---------------------------------------------------------------------------
Mat rectify(const Mat& src, const vector<Point2f>& quad, int outW, int outH) {
    CV_Assert(quad.size() == 4);
    vector<Point2f> dstPts = {
        Point2f(0.f, 0.f),
        Point2f(outW - 1.f, 0.f),
        Point2f(outW - 1.f, outH - 1.f),
        Point2f(0.f, outH - 1.f)};

    Mat H = getPerspectiveTransform(quad, dstPts);
    Mat dst;
    warpPerspective(src, dst, H, Size(outW, outH), INTER_LINEAR, BORDER_CONSTANT, Scalar::all(0));
    return dst;
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
        Mat src(100, 100, CV_8UC1, Scalar(0));
        rectangle(src, Rect(5, 5, 10, 10), Scalar(255), FILLED);
        Point2f c(src.cols / 2.0f - 0.5f, src.rows / 2.0f - 0.5f);

        Mat r90 = rotateAround(src, c, 90.0);
        check(r90.size() == src.size() && r90.type() == CV_8UC1, "16.a mantiene tamaño y tipo");
        check(r90.at<uchar>(89, 10) == 255, "16.a 90° antihorario lleva la marca abajo-izquierda");
        check(r90.at<uchar>(10, 10) == 0, "16.a la posición original queda vacía");

        Mat acc = src.clone();
        for (int i = 0; i < 4; ++i) acc = rotateAround(acc, c, 90.0);
        check(norm(acc, src, NORM_INF) <= 1.0, "16.a 4x90° vuelve al origen");

        Mat half = rotateAround(src, c, 0.0, 0.5);
        check(countNonZero(half) < countNonZero(src), "16.a scale<1 reduce el objeto");
    }
    {
        Mat src(200, 200, CV_8UC1, Scalar(0));
        vector<Point> poly = {Point(40, 30), Point(160, 60), Point(150, 170), Point(30, 130)};
        fillConvexPoly(src, poly, Scalar(255));

        vector<Point2f> quad = {Point2f(40, 30), Point2f(160, 60), Point2f(150, 170), Point2f(30, 130)};
        Mat out = rectify(src, quad, 50, 50);
        check(out.size() == Size(50, 50) && out.type() == CV_8UC1, "16.b devuelve una imagen 50x50 del mismo tipo");
        check(out.at<uchar>(25, 25) == 255, "16.b el centro queda dentro del marcador");
        check(mean(out)[0] > 235.0, "16.b casi todo el resultado es el marcador rectificado");
    }
    {
        Mat src(64, 64, CV_8UC1);
        randu(src, Scalar::all(0), Scalar::all(256));
        vector<Point2f> full = {Point2f(0, 0), Point2f(63, 0), Point2f(63, 63), Point2f(0, 63)};
        Mat out = rectify(src, full, 64, 64);
        check(norm(out, src, NORM_INF) <= 1.0, "16.b esquinas completas -> transformación identidad");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

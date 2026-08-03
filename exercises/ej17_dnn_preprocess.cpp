// EJ 17 — Preprocesado para inferencia: letterbox, blob NCHW y vuelta a coords
//
// CÓMO USARLO
//   1. Rellena las funciones marcadas con  // TODO.
//   2. Compila y ejecuta:   make ej17
//   3. Cronométrate: apunta a ~25 min.
//
// CONTEXTO TIPO ENTREVISTA (el más "de producción" de todos)
//   "Vas a meter la imagen del dron en un detector que espera 640x640. Redimensiona
//    SIN deformar (letterbox con padding), prepárame el tensor NCHW normalizado, y
//    después convierte las cajas que devuelve la red a coordenadas de la imagen
//    original." Esto es literalmente el pre/post-proceso de YOLO en Jetson.
//
// GOTCHAS
//   - Resize directo a 640x640 DEFORMA la imagen y degrada la precisión: hay que
//     escalar con el mismo factor en x e y y rellenar (padding 114 en YOLO).
//   - El tensor de la red es NCHW float (canal primero), no HWC uint8 entrelazado.
//   - La red suele esperar RGB; OpenCV lee BGR -> swapRB.
//   - Al mapear cajas de vuelta hay que RESTAR el padding antes de dividir por la
//     escala, y recortar a los límites de la imagen original.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
using namespace std;
using namespace cv;

// ===========================================================================
// 17.a — letterbox
//   Redimensiona src a target manteniendo la relación de aspecto y centra el
//   resultado sobre un fondo de color `padValue`.
//   scale = min(target.width/w, target.height/h);  nuevo tamaño = round(dim*scale).
//   Devuelve también, por referencia, la escala aplicada y el padding izquierdo
//   y superior (los necesitarás en 17.c).
// ---------------------------------------------------------------------------
Mat letterbox(const Mat& src, Size target, double& scale, int& padLeft, int& padTop,
              int padValue = 114) {
    
    Mat out(target.height, target.width, src.type(), Scalar::all(padValue));
    // Resize the original 
    scale = min((double)target.height / (double)src.rows, 
                (double)target.width / (double)src.cols);
    int newH = round(scale*src.rows);
    int newW = round(scale*src.cols);
    Mat resized;
    resize(src, resized, Size(newW, newH));
    // Place it into the output 
    padLeft = round((float)(target.width - newW) / 2.0);
    padTop = round((float)(target.height - newH) / 2.0);
    Mat roi = out(Rect(padLeft,padTop,newW,newH));
    resized.copyTo(roi);
    return out;
}

// ===========================================================================
// 17.b — toBlobNCHW
//   Convierte una imagen BGR CV_8UC3 (HxW) en un vector float de tamaño
//   3*H*W en layout NCHW (plano de canal 0 entero, luego el 1, luego el 2),
//   multiplicando cada valor por `alpha` (típico 1/255).
//   Si swapRB == true, el orden de canales de salida es R,G,B.
//   Hazlo a mano (es lo que te pedirán explicar), no con blobFromImage.
// ---------------------------------------------------------------------------
vector<float> toBlobNCHW(const Mat& bgr, bool swapRB, float alpha) {
    // TODO
    return {};
}

// ===========================================================================
// 17.c — mapBoxBack
//   Convierte una caja en coordenadas de la imagen letterboxed a coordenadas de
//   la imagen ORIGINAL (tamaño origSize), deshaciendo padding y escala.
//   Recorta el resultado a los límites de la imagen original.
// ---------------------------------------------------------------------------
Rect mapBoxBack(const Rect& box, double scale, int padLeft, int padTop, Size origSize) {
    // TODO
    return Rect();
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
    // --- 17.a ---------------------------------------------------------------
    {
        Mat src(50, 100, CV_8UC3, Scalar(0, 0, 255));   // 100x50 (w x h), rojo
        double s = 0; int pl = 0, pt = 0;
        Mat out = letterbox(src, Size(64, 64), s, pl, pt);

        bool okType = !out.empty() && out.size() == Size(64, 64) && out.type() == CV_8UC3;
        check(okType, "17.a salida 64x64 CV_8UC3");
        check(abs(s - 0.64) < 1e-9, "17.a escala = min(64/100, 64/50) = 0.64");
        check(pl == 0 && pt == 16, "17.a padding centrado: 0 izq, 16 arriba");
        if (okType) {
            check(out.at<Vec3b>(2, 32) == Vec3b(114, 114, 114), "17.a la banda superior es padding");
            check(out.at<Vec3b>(32, 32) == Vec3b(0, 0, 255), "17.a el contenido está en el centro");
        }
        // Imagen ya cuadrada: sin padding
        Mat sq(20, 20, CV_8UC3, Scalar(10, 20, 30));
        Mat o2 = letterbox(sq, Size(40, 40), s, pl, pt);
        check(!o2.empty() && abs(s - 2.0) < 1e-9 && pl == 0 && pt == 0, "17.a cuadrada -> sin padding, escala 2");
    }

    // --- 17.b ---------------------------------------------------------------
    {
        Mat img(2, 2, CV_8UC3);
        img.at<Vec3b>(0, 0) = Vec3b(1, 2, 3);      img.at<Vec3b>(0, 1) = Vec3b(4, 5, 6);
        img.at<Vec3b>(1, 0) = Vec3b(7, 8, 9);      img.at<Vec3b>(1, 1) = Vec3b(10, 11, 12);

        vector<float> b = toBlobNCHW(img, /*swapRB=*/false, /*alpha=*/1.0f);
        check(b.size() == 12, "17.b tamaño 3*H*W");
        // Plano 0 = canal B: 1,4,7,10
        bool plano0 = b.size() == 12 && b[0] == 1 && b[1] == 4 && b[2] == 7 && b[3] == 10;
        bool plano2 = b.size() == 12 && b[8] == 3 && b[9] == 6 && b[10] == 9 && b[11] == 12;
        check(plano0 && plano2, "17.b layout NCHW: canal completo antes del siguiente");

        vector<float> r = toBlobNCHW(img, /*swapRB=*/true, /*alpha=*/1.0f);
        check(r.size() == 12 && r[0] == 3 && r[8] == 1, "17.b swapRB pone R primero y B último");

        // Contraste contra cv::dnn::blobFromImage (la referencia de la industria)
        Mat rnd(8, 5, CV_8UC3);
        randu(rnd, Scalar::all(0), Scalar::all(256));
        vector<float> mine = toBlobNCHW(rnd, true, 1.0f / 255.0f);
        Mat ref = dnn::blobFromImage(rnd, 1.0 / 255.0, Size(), Scalar(), true, false, CV_32F);
        bool same = mine.size() == static_cast<size_t>(ref.total());
        for (size_t i = 0; same && i < mine.size(); ++i)
            same = fabs(mine[i] - ref.ptr<float>()[i]) < 1e-6f;
        check(same, "17.b coincide con cv::dnn::blobFromImage");
    }

    // --- 17.c ---------------------------------------------------------------
    {
        Size orig(100, 50);
        double s = 0.64; int pl = 0, pt = 16;
        check(mapBoxBack(Rect(0, 16, 64, 32), s, pl, pt, orig) == Rect(0, 0, 100, 50),
              "17.c la caja que cubre el contenido -> imagen completa");
        check(mapBoxBack(Rect(0, 16, 32, 32), s, pl, pt, orig) == Rect(0, 0, 50, 50),
              "17.c mitad izquierda -> mitad de la original");
        Rect clipped = mapBoxBack(Rect(0, 0, 64, 64), s, pl, pt, orig);
        check(clipped == Rect(0, 0, 100, 50), "17.c recorta a los límites de la original");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

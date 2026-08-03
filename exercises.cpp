// exercises.cpp — Tanda de práctica (Senior AI SW Eng @ Quantum Systems)
// Foco: C++ moderno + Computer Vision a mano. Sin OpenCV a propósito:
// en coderpad casi siempre implementas el algoritmo, no llamas a la librería.
//
// CÓMO USARLO
//   1. Rellena cada función marcada con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises.cpp -o ex && ./ex
//   3. El harness del final te dice qué pasa y qué falla.
//   4. Cronométrate: apunta a ~10-15 min por ejercicio.
//   5. Solo si te atascas, mira solutions.cpp.
//
// Dificultad creciente (EJ1 warm-up -> EJ7 el más completo).

#include <bits/stdc++.h>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255
struct Box { double x1, y1, x2, y2, score; };

// ===========================================================================
// EJ 1 — Box blur 3x3 (media)
//   Sustituye cada píxel por la media entera (suma/9) de su vecindario 3x3.
//   Bordes: replica el píxel del borde (clamp de coordenadas).
//   Pistas de senior que valoran: cuidado con overflow al sumar (usa int),
//   evita copias innecesarias, comenta la complejidad O(H*W).
// ---------------------------------------------------------------------------
Image boxBlur3(const Image& img) {
    // TODO
    return img;
}

// ===========================================================================
// EJ 2 — Rotar 90° en sentido horario
//   La entrada es H x W; la salida es W x H.
//   Relación: out[x][H-1-y] = img[y][x]
// ---------------------------------------------------------------------------
Image rotate90(const Image& img) {
    // TODO
    return img;
}

// ===========================================================================
// EJ 3 — Contar componentes conexas (blobs)
//   Binariza: píxel "activo" si img[y][x] >= thr.
//   Cuenta cuántas regiones conexas de píxeles activos hay (conectividad-4).
//   Técnica: flood fill (BFS/DFS) o union-find. Cuidado con el stack en DFS
//   recursivo sobre imágenes grandes -> mejor pila explícita o BFS.
// ---------------------------------------------------------------------------
int countBlobs(const Image& img, int thr) {
    // TODO
    return 0;
}

// ===========================================================================
// EJ 4 — IoU (Intersection over Union) de dos cajas
//   Caja = [x1,y1,x2,y2] con x2>x1, y2>y1. Devuelve inter/union en [0,1].
//   Edge cases: cajas disjuntas -> 0; misma caja -> 1; area 0 -> 0.
// ---------------------------------------------------------------------------
double iou(const Box& a, const Box& b) {
    // TODO
    return 0.0;
}

// ===========================================================================
// EJ 5 — Non-Maximum Suppression (NMS)  [usa tu iou() del EJ4]
//   Ordena las cajas por score desc. Recorre: conserva la de mayor score y
//   descarta las que tengan IoU > iou_thr con ella. Repite con las restantes.
//   Devuelve los ÍNDICES conservados (referidos al vector original).
//   Es EL algoritmo de post-proceso en detección de objetos: espera que caiga.
// ---------------------------------------------------------------------------
vector<int> nms(const vector<Box>& boxes, double iou_thr) {
    // TODO
    return {};
}

// ===========================================================================
// EJ 6 — Redimensionar con interpolación bilineal
//   Escala img a (newH x newW). Para cada píxel destino calcula la coordenada
//   fuente con centrado de píxel:  srcX = (x+0.5)*W/newW - 0.5  (idem Y).
//   Mezcla los 4 vecinos con pesos fx, fy. Clamp de coordenadas en bordes.
//   Redondea el resultado a entero.
// ---------------------------------------------------------------------------
Image resizeBilinear(const Image& img, int newH, int newW) {
    // TODO
    return img;
}

// ===========================================================================
// EJ 7 — Magnitud del gradiente Sobel (detección de bordes)
//   Aplica los kernels Sobel Kx (horizontal) y Ky (vertical), calcula
//   mag = sqrt(gx^2 + gy^2), redondea y recorta a 0..255. Bordes con clamp.
//     Kx = [[-1,0,1],[-2,0,2],[-1,0,1]]
//     Ky = [[-1,-2,-1],[0,0,0],[1,2,1]]
// ---------------------------------------------------------------------------
Image sobelMagnitude(const Image& img) {
    // TODO
    return img;
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
    { Image in = {{0,0,0},{0,90,0},{0,0,0}};
      check(boxBlur3(in)[1][1] == 10, "EJ1 blur centro (90/9=10)");
      Image flat(4, vector<int>(4, 50));
      check(boxBlur3(flat)[0][0] == 50, "EJ1 zona uniforme conserva valor"); }

    { Image in = {{1,2,3},{4,5,6}};
      Image out = rotate90(in);
      check(out.size()==3 && (out.empty()?0:out[0].size())==2, "EJ2 dimensiones 90");
      check(out.size()==3 && out[0].size()==2 && out[0][0]==4 && out[0][1]==1 && out[2][1]==3,
            "EJ2 valores 90"); }

    { Image in = {{255,255,0,0,255},{255,0,0,0,255},{0,0,255,0,0},
                  {0,0,0,0,0},{255,0,0,0,255}};
      check(countBlobs(in,128)==5, "EJ3 cuenta 5 blobs (conect-4)");
      Image empty = {{0,0},{0,0}};
      check(countBlobs(empty,128)==0, "EJ3 imagen vacia -> 0"); }

    { Box a{0,0,2,2,1.0}, b{1,1,3,3,1.0};
      check(fabs(iou(a,b) - (1.0/7.0)) < 1e-9, "EJ4 IoU solapamiento parcial");
      Box c{0,0,2,2,1.0}, d{5,5,6,6,1.0};
      check(iou(c,d)==0.0, "EJ4 IoU disjuntas -> 0");
      check(fabs(iou(a,a)-1.0)<1e-9, "EJ4 IoU consigo misma -> 1"); }

    { vector<Box> bs = {{0,0,2,2,0.9},{0.1,0.1,2.1,2.1,0.8},{5,5,7,7,0.7}};
      auto k = nms(bs, 0.5);
      sort(k.begin(), k.end());
      check(k.size()==2 && k[0]==0 && k[1]==2, "EJ5 NMS conserva {0,2}"); }

    { Image in = {{0,0},{0,0}};
      check(resizeBilinear(in,4,4).size()==4 && resizeBilinear(in,4,4)[2][2]==0,
            "EJ6 uniforme 0 se mantiene");
      Image in2 = {{0,10},{0,10}};
      Image up = resizeBilinear(in2,2,4);
      check(up.size()==2 && up[0].size()==4, "EJ6 dimensiones destino");
      check(up.size()==2 && up[0].size()==4 && up[0][0] <= up[0][3],
            "EJ6 gradiente horizontal creciente"); }

    { Image in = {{0,0,255,255},{0,0,255,255},{0,0,255,255},{0,0,255,255}};
      Image m = sobelMagnitude(in);
      check(m.size()==4 && m[0].size()==4 && m[1][1] > m[1][0],
            "EJ7 magnitud mayor junto al borde");
      check(m.size()==4 && m[0][0] >= 0 && m[3][3] <= 255, "EJ7 valores en rango 0..255"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

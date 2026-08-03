// solutions.cpp — Soluciones de referencia (Senior AI SW Eng prep)
// Compilar:  g++ -std=c++17 -O2 -Wall solutions.cpp -o sol && ./sol
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <bits/stdc++.h>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255
struct Box { double x1, y1, x2, y2, score; };

// ---------------------------------------------------------------------------
// EJ 1 — Box blur 3x3 (media). Bordes: replicar el píxel del borde (clamp).
Image boxBlur3(const Image& img) {
    int H = img.size(), W = H ? img[0].size() : 0;
    Image out(H, vector<int>(W, 0));
    auto clamp = [](int v, int lo, int hi){ return max(lo, min(v, hi)); };
    for (int y = 0; y < H; ++y)
        for (int x = 0; x < W; ++x) {
            int sum = 0;
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx)
                    sum += img[clamp(y+dy,0,H-1)][clamp(x+dx,0,W-1)];
            out[y][x] = sum / 9;   // división entera
        }
    return out;
}

// ---------------------------------------------------------------------------
// EJ 2 — Rotar imagen 90° en sentido horario. Devuelve nueva matriz.
Image rotate90(const Image& img) {
    int H = img.size(), W = H ? img[0].size() : 0;
    Image out(W, vector<int>(H, 0));
    for (int y = 0; y < H; ++y)
        for (int x = 0; x < W; ++x)
            out[x][H-1-y] = img[y][x];
    return out;
}

// ---------------------------------------------------------------------------
// EJ 3 — Binariza (>= thr -> 1, si no 0) y cuenta componentes conexas de 1s
// con conectividad-4 (flood fill).
int countBlobs(const Image& img, int thr) {
    int H = img.size(), W = H ? img[0].size() : 0;
    vector<vector<char>> seen(H, vector<char>(W, 0));
    int count = 0;
    int dx[] = {1,-1,0,0}, dy[] = {0,0,1,-1};
    for (int sy = 0; sy < H; ++sy)
        for (int sx = 0; sx < W; ++sx) {
            if (img[sy][sx] < thr || seen[sy][sx]) continue;
            ++count;
            stack<pair<int,int>> st;
            st.push({sy,sx}); seen[sy][sx] = 1;
            while (!st.empty()) {
                auto [y,x] = st.top(); st.pop();
                for (int k = 0; k < 4; ++k) {
                    int ny = y+dy[k], nx = x+dx[k];
                    if (ny<0||ny>=H||nx<0||nx>=W) continue;
                    if (img[ny][nx] >= thr && !seen[ny][nx]) {
                        seen[ny][nx] = 1; st.push({ny,nx});
                    }
                }
            }
        }
    return count;
}

// ---------------------------------------------------------------------------
// EJ 4 — IoU (Intersection over Union) de dos cajas [x1,y1,x2,y2].
double iou(const Box& a, const Box& b) {
    double ix1 = max(a.x1, b.x1), iy1 = max(a.y1, b.y1);
    double ix2 = min(a.x2, b.x2), iy2 = min(a.y2, b.y2);
    double iw = max(0.0, ix2 - ix1), ih = max(0.0, iy2 - iy1);
    double inter = iw * ih;
    double areaA = max(0.0,(a.x2-a.x1)) * max(0.0,(a.y2-a.y1));
    double areaB = max(0.0,(b.x2-b.x1)) * max(0.0,(b.y2-b.y1));
    double uni = areaA + areaB - inter;
    return uni <= 0.0 ? 0.0 : inter / uni;
}

// ---------------------------------------------------------------------------
// EJ 5 — Non-Maximum Suppression. Devuelve índices conservados, ordenados por
// score descendente, eliminando cajas con IoU > iou_thr respecto a una mejor.
vector<int> nms(const vector<Box>& boxes, double iou_thr) {
    int n = boxes.size();
    vector<int> idx(n);
    iota(idx.begin(), idx.end(), 0);
    sort(idx.begin(), idx.end(), [&](int i, int j){
        return boxes[i].score > boxes[j].score; });
    vector<char> removed(n, 0);
    vector<int> keep;
    for (int ii = 0; ii < n; ++ii) {
        int i = idx[ii];
        if (removed[i]) continue;
        keep.push_back(i);
        for (int jj = ii+1; jj < n; ++jj) {
            int j = idx[jj];
            if (removed[j]) continue;
            if (iou(boxes[i], boxes[j]) > iou_thr) removed[j] = 1;
        }
    }
    return keep;
}

// ---------------------------------------------------------------------------
// EJ 6 — Redimensiona a (newH,newW) con interpolación bilineal.
// Mapeo estándar: srcX = (x+0.5)*W/newW - 0.5 (align pixel centers).
Image resizeBilinear(const Image& img, int newH, int newW) {
    int H = img.size(), W = H ? img[0].size() : 0;
    Image out(newH, vector<int>(newW, 0));
    auto clampi = [](int v, int lo, int hi){ return max(lo, min(v, hi)); };
    for (int y = 0; y < newH; ++y) {
        double sy = (y + 0.5) * H / newH - 0.5;
        int y0 = (int)floor(sy); double fy = sy - y0;
        int y0c = clampi(y0,0,H-1), y1c = clampi(y0+1,0,H-1);
        for (int x = 0; x < newW; ++x) {
            double sx = (x + 0.5) * W / newW - 0.5;
            int x0 = (int)floor(sx); double fx = sx - x0;
            int x0c = clampi(x0,0,W-1), x1c = clampi(x0+1,0,W-1);
            double top = img[y0c][x0c]*(1-fx) + img[y0c][x1c]*fx;
            double bot = img[y1c][x0c]*(1-fx) + img[y1c][x1c]*fx;
            out[y][x] = (int)llround(top*(1-fy) + bot*fy);
        }
    }
    return out;
}

// ---------------------------------------------------------------------------
// EJ 7 — Magnitud del gradiente Sobel. Bordes con clamp. Devuelve
// round(sqrt(gx^2+gy^2)) recortado a 0..255.
//   Kx = [[-1,0,1],[-2,0,2],[-1,0,1]]   Ky = Kx transpuesto (vertical)
Image sobelMagnitude(const Image& img) {
    int H = img.size(), W = H ? img[0].size() : 0;
    Image out(H, vector<int>(W, 0));
    int Kx[3][3] = {{-1,0,1},{-2,0,2},{-1,0,1}};
    int Ky[3][3] = {{-1,-2,-1},{0,0,0},{1,2,1}};
    auto clampi = [](int v, int lo, int hi){ return max(lo, min(v, hi)); };
    for (int y = 0; y < H; ++y)
        for (int x = 0; x < W; ++x) {
            int gx = 0, gy = 0;
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    int v = img[clampi(y+dy,0,H-1)][clampi(x+dx,0,W-1)];
                    gx += Kx[dy+1][dx+1]*v;
                    gy += Ky[dy+1][dx+1]*v;
                }
            int mag = (int)llround(sqrt((double)gx*gx + (double)gy*gy));
            out[y][x] = clampi(mag, 0, 255);
        }
    return out;
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
    // EJ1
    {
        Image in = {{0,0,0},{0,90,0},{0,0,0}};
        Image out = boxBlur3(in);
        check(out[1][1] == 10, "EJ1 blur centro (90/9=10)");
        Image flat(4, vector<int>(4, 50));
        check(boxBlur3(flat)[0][0] == 50, "EJ1 blur zona uniforme conserva valor");
    }
    // EJ2
    {
        Image in = {{1,2,3},{4,5,6}};      // 2x3
        Image out = rotate90(in);           // 3x2 esperado: {{4,1},{5,2},{6,3}}
        check(out.size()==3 && out[0].size()==2, "EJ2 dimensiones 90");
        check(out[0][0]==4 && out[0][1]==1 && out[2][1]==3, "EJ2 valores 90");
    }
    // EJ3
    {
        Image in = {
            {255,255,0,0,255},
            {255,0,0,0,255},
            {0,0,255,0,0},
            {0,0,0,0,0},
            {255,0,0,0,255}};
        check(countBlobs(in,128)==5, "EJ3 cuenta 5 blobs (conect-4)");
        Image empty = {{0,0},{0,0}};
        check(countBlobs(empty,128)==0, "EJ3 imagen vacia -> 0");
    }
    // EJ4
    {
        Box a{0,0,2,2,1.0}, b{1,1,3,3,1.0};
        check(fabs(iou(a,b) - (1.0/7.0)) < 1e-9, "EJ4 IoU solapamiento parcial");
        Box c{0,0,2,2,1.0}, d{5,5,6,6,1.0};
        check(iou(c,d)==0.0, "EJ4 IoU disjuntas -> 0");
        check(fabs(iou(a,a)-1.0)<1e-9, "EJ4 IoU consigo misma -> 1");
    }
    // EJ5
    {
        vector<Box> bs = {
            {0,0,2,2,0.9}, {0.1,0.1,2.1,2.1,0.8},  // muy solapadas -> se queda la 0
            {5,5,7,7,0.7}};                          // separada -> se queda
        auto k = nms(bs, 0.5);
        sort(k.begin(), k.end());
        check(k.size()==2 && k[0]==0 && k[1]==2, "EJ5 NMS conserva {0,2}");
    }
    // EJ6
    {
        Image in = {{0,0},{0,0}};
        check(resizeBilinear(in,4,4)[2][2]==0, "EJ6 uniforme 0 se mantiene");
        Image in2 = {{0,10},{0,10}};
        Image up = resizeBilinear(in2,2,4);   // ancho x2
        check(up.size()==2 && up[0].size()==4, "EJ6 dimensiones destino");
        check(up[0][0] <= up[0][3], "EJ6 gradiente horizontal creciente");
    }
    // EJ7
    {
        // Borde vertical: mitad izq 0, mitad der 255 -> gradiente fuerte en el centro
        Image in = {
            {0,0,255,255},
            {0,0,255,255},
            {0,0,255,255},
            {0,0,255,255}};
        Image m = sobelMagnitude(in);
        check(m[1][1] > m[1][0], "EJ7 magnitud mayor junto al borde");
        check(m[0][0] >= 0 && m[3][3] <= 255, "EJ7 valores en rango 0..255");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

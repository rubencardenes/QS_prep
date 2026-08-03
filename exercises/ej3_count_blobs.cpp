// EJ 3 — Contar componentes conexas (blobs)
//
// CÓMO USARLO
//   1. Rellena la función marcada con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej3_count_blobs.cpp -o ej3 && ./ej3
//   3. Cronométrate: apunta a ~10-15 min.
//   4. Solo si te atascas, mira solutions/ej3_count_blobs.cpp.

#include <algorithm>
#include <iostream>
#include <queue>
#include <stack>
#include <string>
#include <utility>
#include <vector>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255

// ===========================================================================
// EJ 3 — Contar componentes conexas (blobs)
//   Binariza: píxel "activo" si img[y][x] >= thr.
//   Cuenta cuántas regiones conexas de píxeles activos hay (conectividad-4).
//   Técnica: flood fill (BFS/DFS) o union-find. Cuidado con el stack en DFS
//   recursivo sobre imágenes grandes -> mejor pila explícita o BFS.
// ---------------------------------------------------------------------------
void traverse(const Image& img, int x, int y, Image& mask, int thr) {
    const int H = img.size();
    const int W = img[0].size();
    int dx[] = {0, 0, -1, 1};
    int dy[] = {-1, 1, 0, 0};
    queue<pair<int, int>> my_queue;
    my_queue.push({x,y});
    while (my_queue.size() > 0) {
        auto front = my_queue.front();
        x = front.first;
        y = front.second;
        my_queue.pop();
        for (int i = 0; i< 4; i++) {
            int ny = y+dy[i],nx = x+dx[i];
            if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
            if (mask[ny][nx] == 0 && img[ny][nx] > thr) {
                my_queue.push({nx , ny});
                mask[ny][nx] = 1;
            }
        } 
    } 
      
}

int countBlobs(const Image& img, int thr) {
    int num_cc = 0;
    const int H = img.size();
    const int W = img[0].size();
    Image mask_visited(H, vector<int>(W)); 
    for (int y=0; y < H; ++y) {
        for (int x=0; x < W; ++x) {
            if (img[y][x] > thr && mask_visited[y][x] == 0) {
                mask_visited[y][x] = 1;
                num_cc++;
                traverse(img, x, y, mask_visited, thr); 
            }
        }
    }
    return num_cc;
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
    { Image in = {{255,255,0,0,255},
                  {255,0,0,0,255},
                  {0,0,255,0,0},
                  {0,0,0,0,0},
                  {255,0,0,0,255}};
      check(countBlobs(in,128)==5, "EJ3 cuenta 5 blobs (conect-4)");
      Image empty = {{0,0},{0,0}};
      check(countBlobs(empty,128)==0, "EJ3 imagen vacia -> 0"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

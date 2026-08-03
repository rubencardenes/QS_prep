// EJ 21 — Tracker por IoU: asociación de detecciones entre frames (SORT simplificado)
//
// CÓMO USARLO
//   1. Rellena el método marcado con  // TODO.
//   2. Compila y ejecuta:   make ej21
//   3. Cronométrate: apunta a ~30 min.
//
// CONTEXTO TIPO ENTREVISTA
//   "El detector corre por frame y no sabe nada del anterior: te da cajas sin
//    identidad. Necesitamos IDs estables para contar objetos y estimar su
//    velocidad. Implementa la asociación frame a frame."
//
//   Esto es el núcleo de SORT/ByteTrack sin el filtro de Kalman. Si te sobra
//   tiempo, la extensión natural es predecir la caja del track con velocidad
//   constante antes de asociar, y ahí es donde entra el Kalman.
//
// REGLAS DE LA ASOCIACIÓN (greedy)
//   1. Calcula el IoU de todos los pares (track, detección).
//   2. Descarta los pares con IoU < iouThr.
//   3. Recorre los pares de mayor a menor IoU y empareja si ni el track ni la
//      detección están ya emparejados (desempate: menor id de track, luego
//      menor índice de detección — el resultado debe ser DETERMINISTA).
//   4. Track emparejado -> actualiza caja, ++hits, missed = 0.
//      Track sin pareja  -> ++missed; se elimina cuando missed > maxMissed.
//      Detección sin pareja -> nuevo track con el siguiente id libre.
//
// GOTCHAS
//   - El greedy no es óptimo (lo óptimo es el algoritmo húngaro, O(n^3)); para
//     pocas cajas por frame el greedy va sobrado y es lo que usa SORT en la
//     práctica. Mencionar la diferencia es señal de que sabes de qué hablas.
//   - Los IDs no se reutilizan nunca: un contador que solo sube.
//   - Ojo al orden de las operaciones: si borras los tracks perdidos antes de
//     crear los nuevos, los ids cambian. Crea siempre en orden de detección.

#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

struct Box { double x1, y1, x2, y2; };

struct Track {
    int id;
    Box box;
    int hits;      // frames en los que se ha emparejado (incluido el de creación)
    int missed;    // frames consecutivos sin emparejar
};

// --- Dado: IoU entre dos cajas (ya lo implementaste en el EJ 4) -------------
static double iou(const Box& a, const Box& b) {
    double ix1 = max(a.x1, b.x1), iy1 = max(a.y1, b.y1);
    double ix2 = min(a.x2, b.x2), iy2 = min(a.y2, b.y2);
    double iw = max(0.0, ix2 - ix1), ih = max(0.0, iy2 - iy1);
    double inter = iw * ih;
    double areaA = max(0.0, a.x2 - a.x1) * max(0.0, a.y2 - a.y1);
    double areaB = max(0.0, b.x2 - b.x1) * max(0.0, b.y2 - b.y1);
    double uni = areaA + areaB - inter;
    return uni <= 0.0 ? 0.0 : inter / uni;
}

// ===========================================================================
// 21 — IouTracker
// ---------------------------------------------------------------------------
class IouTracker {
public:
    explicit IouTracker(double iouThr = 0.3, int maxMissed = 1)
        : iouThr_(iouThr), maxMissed_(maxMissed) {}

    // Procesa un frame y devuelve los tracks vivos, ordenados por id ascendente.
    vector<Track> update(const vector<Box>& dets) {
        // TODO
        vector<int> alive_track_ids;
        for (int i=0;i<tracks_.size()-1;i++) {
            for (int j=0;j<dets.size()-1;j++) {
                if (iou(tracks_[i].box, dets[j]) > iouThr_) {
                    alive_track_ids.push_back(i);
                    tracks_[i].hits++;
                }
            }
        }
        sort(tracks_.begin(), tracks_.end(), [](int i, int j, vector<int>tracks_alive){
            return tracks_alive[i] < tracks_alive[j]};);
        return tracks_;
    }

private:
    vector<Track> tracks_;
    int nextId_ = 0;
    double iouThr_;
    int maxMissed_;
};

// ===========================================================================
//                        TEST HARNESS (no tocar)
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

static bool sameBox(const Box& a, const Box& b) {
    return abs(a.x1-b.x1) < 1e-9 && abs(a.y1-b.y1) < 1e-9 &&
           abs(a.x2-b.x2) < 1e-9 && abs(a.y2-b.y2) < 1e-9;
}

int main() {
    // --- identidad estable a lo largo de los frames -------------------------
    {
        IouTracker t(0.3, 1);
        Box A{0,0,10,10}, B{100,100,110,110};

        vector<Track> f1 = t.update({A, B});
        check(f1.size() == 2, "21 frame 1: dos detecciones -> dos tracks");
        if (f1.size() == 2) {
            check(f1[0].id == 0 && f1[1].id == 1, "21 ids asignados en orden de detección");
            check(f1[0].hits == 1 && f1[0].missed == 0, "21 track nuevo con hits=1, missed=0");
        }

        vector<Track> f2 = t.update({{1,0,11,10}, {101,100,111,110}});
        check(f2.size() == 2 && f2[0].id == 0 && f2[1].id == 1, "21 frame 2: los ids se mantienen");
        check(f2.size() == 2 && f2[0].hits == 2 && f2[0].missed == 0, "21 hits incrementa al emparejar");
        check(f2.size() == 2 && sameBox(f2[0].box, {1,0,11,10}), "21 la caja se actualiza a la detección");
    }

    // --- desaparición y expiración ------------------------------------------
    {
        IouTracker t(0.3, 1);
        t.update({{0,0,10,10}, {100,100,110,110}});
        vector<Track> f2 = t.update({{0,0,10,10}});
        check(f2.size() == 2, "21 un track perdido sobrevive mientras missed <= maxMissed");
        auto it = find_if(f2.begin(), f2.end(), [](const Track& tr){ return tr.id == 1; });
        check(it != f2.end() && it->missed == 1, "21 el track perdido cuenta missed=1");
        check(it != f2.end() && sameBox(it->box, {100,100,110,110}), "21 conserva su última caja");

        vector<Track> f3 = t.update({{0,0,10,10}});
        check(f3.size() == 1 && f3[0].id == 0, "21 se elimina cuando missed > maxMissed");

        vector<Track> f4 = t.update({{0,0,10,10}, {200,200,210,210}});
        check(f4.size() == 2 && f4[1].id == 2, "21 los ids no se reutilizan");
    }

    // --- el greedy elige la mejor pareja, no la primera ----------------------
    {
        IouTracker t(0.3, 1);
        t.update({{0,0,10,10}, {5,0,15,10}});          // track 0 y track 1
        // Cruzadas a propósito: track0-det1 = 1.00, track1-det0 = 0.82,
        //                       track0-det0 = 0.43, track1-det1 = 0.33
        vector<Track> f2 = t.update({{4,0,14,10}, {0,0,10,10}});
        check(f2.size() == 2, "21 dos tracks siguen vivos tras el cruce");
        check(f2.size() == 2 && sameBox(f2[0].box, {0,0,10,10}), "21 track 0 se queda la pareja de IoU 1.0");
        check(f2.size() == 2 && sameBox(f2[1].box, {4,0,14,10}), "21 track 1 se queda la otra");
    }

    // --- umbral y casos degenerados ------------------------------------------
    {
        IouTracker t(0.5, 1);
        t.update({{0,0,10,10}});
        // IoU = 25/175 = 0.14 < 0.5 -> no empareja: track nuevo y el viejo pierde
        vector<Track> f2 = t.update({{5,5,15,15}});
        check(f2.size() == 2, "21 por debajo del umbral se crea un track nuevo");
        check(f2.size() == 2 && f2[0].missed == 1 && f2[1].id == 1, "21 el viejo queda como perdido");
    }
    {
        IouTracker t;
        check(t.update({}).empty(), "21 sin detecciones y sin tracks -> vacío");
        t.update({{0,0,10,10}});
        check(t.update({}).size() == 1, "21 frame vacío no borra un track de golpe");
        check(t.update({}).empty(), "21 ...pero expira al superar maxMissed");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}

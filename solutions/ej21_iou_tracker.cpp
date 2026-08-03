// EJ 21 — Tracker por IoU (SORT simplificado) — solución de referencia
// Compilar:  make sol21
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

struct Box { double x1, y1, x2, y2; };

struct Track {
    int id;
    Box box;
    int hits;
    int missed;
};

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

// ---------------------------------------------------------------------------
// El algoritmo tiene tres fases bien separadas — mantenerlas separadas es lo
// que hace que esto se pueda leer y depurar:
//   1) construir la matriz de coste (aquí, solo los pares por encima del umbral)
//   2) resolver la asignación (greedy por IoU descendente)
//   3) aplicar el resultado: actualizar, envejecer, crear, expirar
//
// Coste: O(T*D log(T*D)) por el sort. Con T,D ~ decenas es irrelevante. Si
// creciera, lo suyo es el algoritmo húngaro (asignación óptima, O(n^3)) — que
// es exactamente lo que hace SORT con scipy.linear_sum_assignment.
// ---------------------------------------------------------------------------
class IouTracker {
public:
    explicit IouTracker(double iouThr = 0.3, int maxMissed = 1)
        : iouThr_(iouThr), maxMissed_(maxMissed) {}

    vector<Track> update(const vector<Box>& dets) {
        struct Cand { double iou; int t; int d; };
        vector<Cand> cand;
        for (size_t i = 0; i < tracks_.size(); ++i)
            for (size_t j = 0; j < dets.size(); ++j) {
                double v = iou(tracks_[i].box, dets[j]);
                if (v >= iouThr_) cand.push_back({v, (int)i, (int)j});
            }

        // Orden total: IoU desc, y desempates estables -> salida reproducible.
        sort(cand.begin(), cand.end(), [this](const Cand& a, const Cand& b) {
            if (a.iou != b.iou) return a.iou > b.iou;
            if (tracks_[a.t].id != tracks_[b.t].id) return tracks_[a.t].id < tracks_[b.t].id;
            return a.d < b.d;
        });

        vector<int> matchOf(tracks_.size(), -1);
        vector<char> detUsed(dets.size(), 0);
        for (const Cand& c : cand) {
            if (matchOf[c.t] != -1 || detUsed[c.d]) continue;   // ya emparejados
            matchOf[c.t] = c.d;
            detUsed[c.d] = 1;
        }

        vector<Track> alive;
        alive.reserve(tracks_.size() + dets.size());
        for (size_t i = 0; i < tracks_.size(); ++i) {
            Track tr = tracks_[i];
            if (matchOf[i] >= 0) {
                tr.box = dets[matchOf[i]];
                ++tr.hits;
                tr.missed = 0;
                alive.push_back(tr);
            } else if (++tr.missed <= maxMissed_) {
                alive.push_back(tr);            // sigue vivo con su última caja
            }                                   // si no, expira (no se copia)
        }
        // Los nuevos, en orden de detección: así los ids son predecibles.
        for (size_t j = 0; j < dets.size(); ++j)
            if (!detUsed[j]) alive.push_back({nextId_++, dets[j], 1, 0});

        tracks_ = std::move(alive);
        sort(tracks_.begin(), tracks_.end(),
             [](const Track& a, const Track& b) { return a.id < b.id; });
        return tracks_;
    }

private:
    vector<Track> tracks_;
    int nextId_ = 0;
    double iouThr_;
    int maxMissed_;
};

// ===========================================================================
//                               TEST HARNESS
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
    {
        IouTracker t(0.3, 1);
        Box A{0,0,10,10}, B{100,100,110,110};

        vector<Track> f1 = t.update({A, B});
        check(f1.size() == 2, "21 frame 1: dos detecciones -> dos tracks");
        check(f1[0].id == 0 && f1[1].id == 1, "21 ids asignados en orden de detección");
        check(f1[0].hits == 1 && f1[0].missed == 0, "21 track nuevo con hits=1, missed=0");

        vector<Track> f2 = t.update({{1,0,11,10}, {101,100,111,110}});
        check(f2.size() == 2 && f2[0].id == 0 && f2[1].id == 1, "21 frame 2: los ids se mantienen");
        check(f2[0].hits == 2 && f2[0].missed == 0, "21 hits incrementa al emparejar");
        check(sameBox(f2[0].box, {1,0,11,10}), "21 la caja se actualiza a la detección");
    }
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
    {
        IouTracker t(0.3, 1);
        t.update({{0,0,10,10}, {5,0,15,10}});
        vector<Track> f2 = t.update({{4,0,14,10}, {0,0,10,10}});
        check(f2.size() == 2, "21 dos tracks siguen vivos tras el cruce");
        check(sameBox(f2[0].box, {0,0,10,10}), "21 track 0 se queda la pareja de IoU 1.0");
        check(sameBox(f2[1].box, {4,0,14,10}), "21 track 1 se queda la otra");
    }
    {
        IouTracker t(0.5, 1);
        t.update({{0,0,10,10}});
        vector<Track> f2 = t.update({{5,5,15,15}});
        check(f2.size() == 2, "21 por debajo del umbral se crea un track nuevo");
        check(f2[0].missed == 1 && f2[1].id == 1, "21 el viejo queda como perdido");
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

# Ejercicios de preparación — Quantum Systems
#
#   make ej3          compila y ejecuta el ejercicio 3 (tu versión)
#   make sol3         compila y ejecuta la solución del ejercicio 3
#   make exercises    compila y ejecuta todos los ejercicios
#   make solutions    compila y ejecuta todas las soluciones
#   make clean        borra los binarios
#
# Bloque 1-2 (ej1-ej12): C++ puro, sin dependencias.
# Bloque 3  (ej13-ej17): OpenCV. Necesita opencv4 vía pkg-config
#                        (macOS: brew install opencv).

CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -pthread
BUILD    := build

# Homebrew ya sirve OpenCV 5; en Linux/Jetson lo normal sigue siendo opencv4.
CV_PKG   := $(shell pkg-config --exists opencv5 && echo opencv5 || echo opencv4)
CV_FLAGS := $(shell pkg-config --cflags --libs $(CV_PKG) 2>/dev/null)

NUMS    := 1 2 3 4 5 6 7 8 9 10 11 12 18 19 20 21
CV_NUMS := 13 14 15 16 17 22
ALL_NUMS := $(NUMS) $(CV_NUMS)

.PHONY: all exercises solutions cv-check clean \
        $(addprefix ej,$(ALL_NUMS)) $(addprefix sol,$(ALL_NUMS))

all: solutions

# --- Atajos por ejercicio: make ej3 / make sol3 -----------------------------
# $(2) = flags extra de compilación (OpenCV para el bloque 3)
define RULE_ONE
ej$(1): $$(BUILD)/ej$(1)
	-@./$$(BUILD)/ej$(1)

sol$(1): $$(BUILD)/sol$(1)
	@./$$(BUILD)/sol$(1)

$$(BUILD)/ej$(1): $$(wildcard exercises/ej$(1)_*.cpp) | $$(BUILD)
	$$(CXX) $$(CXXFLAGS) $$< -o $$@ $(2)

$$(BUILD)/sol$(1): $$(wildcard solutions/ej$(1)_*.cpp) | $$(BUILD)
	$$(CXX) $$(CXXFLAGS) $$< -o $$@ $(2)
endef
$(foreach n,$(NUMS),$(eval $(call RULE_ONE,$(n))))
$(foreach n,$(CV_NUMS),$(eval $(call RULE_ONE,$(n),$$(CV_FLAGS))))

exercises: $(addprefix ej,$(ALL_NUMS))
solutions: $(addprefix sol,$(ALL_NUMS))

# Comprueba que OpenCV está disponible antes de pelearte con el compilador.
cv-check:
	@pkg-config --modversion $(CV_PKG) >/dev/null 2>&1 \
	  && echo "OpenCV $$(pkg-config --modversion $(CV_PKG)) OK ($(CV_PKG))" \
	  || echo "OpenCV NO encontrado. macOS: brew install opencv"

$(BUILD):
	@mkdir -p $(BUILD)

clean:
	@rm -rf $(BUILD)

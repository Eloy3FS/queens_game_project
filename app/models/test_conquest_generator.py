# %% [markdown]
# # Depuración Interactiva del Conquest Generator
# 
# Este notebook usa `record_steps=True` y muestra todos los estados intermedios (conquistas y pasos lógicos)
# con un slider muy ágil, gracias a caching de imágenes y `ipywidgets.interact`.
# 

# %%
# Si aún no lo tienes, descomenta e instala:
# !pip install ipywidgets pillow

import sys, os
# Si este notebook está en un subdirectorio, ajusta la ruta:
# os.chdir('..')
sys.path.insert(0, os.getcwd())

from conquest_generator import generate_conquest_board  # o la ruta correcta
from PIL import Image
import numpy as np
import ipywidgets as widgets
from IPython.display import display, Markdown, clear_output
from functools import lru_cache
from collections import OrderedDict

from app.models.resoution import SolverState


# %%
from copy import deepcopy

# Mapea número de paso a descripción
RULE_NAMES = {
    1: 'Deducción por color único',
    2: 'Deducción por fila',
    3: 'Eliminación por uniformidad',
    4: 'Naked sets',
    5: 'Seguridad global',           # ← step5_and_6
}


def record_resolution_steps(colored_board):
    """
    Ejecuta la resolución barata-primero y devuelve, en orden,
    los nombres de las reglas que produjeron **algún** cambio.
    """
    solver = SolverState(colored_board)
    seq = solver.propagate()                  # p. ej. [1, 2, 1, 3, 5]
    return [RULE_NAMES[s] for s in seq]


def _diff(prev_cand, prev_q, now_cand, now_q):
    """
    Devuelve (eliminated, placed) comparando dos instantáneas.
    """
    N = len(prev_cand)
    eliminated = [
        (r, c)
        for r in range(N) for c in range(N)
        if prev_cand[r][c] and not now_cand[r][c]
    ]
    placed = [
        (r, c)
        for r in range(N) for c in range(N)
        if now_q[r][c] and not prev_q[r][c]
    ]
    return eliminated, placed


def record_step_changes(colored_board):
    """
    Igual que antes pero siguiendo la lógica de `propagate()`:
    se vuelve a empezar **solo** cuando un paso ≥ 2 cambió algo.
    """
    solver = SolverState(colored_board)
    N = solver.N
    changes = []

    while True:
        any_changed = False

        # ---------- Paso 1 (no reinicia ciclo) ----------
        prev_cand, prev_q = [row[:] for row in solver.candidates], [row[:] for row in solver.queens]
        if solver.step1():
            any_changed = True
            elim, plc = _diff(prev_cand, prev_q, solver.candidates, solver.queens)
            changes.append({"label": 1, "eliminations": elim, "placements": plc})

        # ---------- Paso 2 ----------
        prev_cand, prev_q = [row[:] for row in solver.candidates], [row[:] for row in solver.queens]
        if solver.step2():
            any_changed = True
            elim, plc = _diff(prev_cand, prev_q, solver.candidates, solver.queens)
            changes.append({"label": 2, "eliminations": elim, "placements": plc})
            continue          # volver a paso 1

        # ---------- Paso 3 ----------
        prev_cand, prev_q = [row[:] for row in solver.candidates], [row[:] for row in solver.queens]
        if solver.step3():
            any_changed = True
            elim, plc = _diff(prev_cand, prev_q, solver.candidates, solver.queens)
            changes.append({"label": 3, "eliminations": elim, "placements": plc})
            continue

        # ---------- Paso 4 ----------
        prev_cand, prev_q = [row[:] for row in solver.candidates], [row[:] for row in solver.queens]
        if solver.step4():
            any_changed = True
            elim, plc = _diff(prev_cand, prev_q, solver.candidates, solver.queens)
            changes.append({"label": 4, "eliminations": elim, "placements": plc})
            continue

        # ---------- Paso 5-6 ----------
        prev_cand, prev_q = [row[:] for row in solver.candidates], [row[:] for row in solver.queens]
        if solver.step5_and_6():
            any_changed = True
            elim, plc = _diff(prev_cand, prev_q, solver.candidates, solver.queens)
            changes.append({"label": 5, "eliminations": elim, "placements": plc})
            continue

        if not any_changed:
            break

    # Convierto labels a texto humano
    for d in changes:
        d["label"] = RULE_NAMES[d["label"]]
    return changes





# %%
# Parámetros
N = 8
debug = True

# Ejecuta la generación con record_steps=True
sol, final_board, iterations, successful, reason, history = generate_conquest_board(
    n=N, debug=debug, record_steps=True
)

print(f"Solución oficial: {sol}")
print(f"Iteraciones: {iterations}, Conquistas: {successful}, Motivo: {reason}")
print(f"Estados registrados: {len(history)}")


# %%
# Creamos un map para agrupar por contenido de board
group_map = OrderedDict()
for label, board in history:
    key = tuple(tuple(row) for row in board)
    if key not in group_map:
        group_map[key] = {"board": board, "labels": []}
    group_map[key]["labels"].append(label)

# Lista de entradas ordenadas
entries = list(group_map.values())


# Para el primer tablero (o el seleccionado), generamos todos los sub-pasos:
# Aquí usaremos siempre `entries[idx]["board"]` cuando llamemos.
# Pero vamos a precachear para todos los entries:
entries_changes = []
for entry in entries:
    changes = record_step_changes(entry["board"])
    entries_changes.append(changes)

print(f"Tableros distintos tras cada cambio: {len(entries)}")




# %%
@lru_cache(maxsize=None)
def get_board_image(idx: int):
    """
    Devuelve (board, labels, PIL.Image) escalada 30×30 px por celda.
    """
    entry = entries[idx]
    board = entry["board"]
    labels = entry["labels"]
    arr = np.array(board, dtype=np.uint8)            # (N,N,3)
    img = Image.fromarray(arr).resize((N*30, N*30), Image.NEAREST)
    return board, labels, img



def draw_overlay(idx_board: int, idx_step: int):
    """
    Dibuja el tablero base y superpone de forma acumulativa
    todas las eliminaciones (negro) y colocaciones (blanco)
    desde el paso 0 hasta idx_step.
    """
    # Tablero base coloreado
    board = entries[idx_board]["board"]
    img_base = Image.fromarray(
        np.array(board, dtype=np.uint8)
    ).resize((N*30, N*30), Image.NEAREST).convert("RGBA")
    
    overlay = img_base.copy()
    cell = 30
    
    # Recorremos todos los sub-pasos hasta idx_step (inclusive)
    for k in range(idx_step + 1):
        step = entries_changes[idx_board][k]
        # Primero eliminaciones = cruces negras
        for (r, c) in step["eliminations"]:
            x0, y0 = c * cell, r * cell
            for y in range(y0, y0 + cell):
                for x in range(x0, x0 + cell):
                    overlay.putpixel((x, y), (0, 0, 0, 255))
        # Luego colocaciones = cuadrados blancos
        for (r, c) in step["placements"]:
            x0, y0 = c * cell, r * cell
            for y in range(y0, y0 + cell):
                for x in range(x0, x0 + cell):
                    overlay.putpixel((x, y), (255, 255, 255, 255))
    
    return overlay



# %%
out = widgets.Output()

def show_board(idx: int):
    with out:
        clear_output(wait=True)
        
        # 1) Mostramos el tablero
        entry = entries[idx]
        board = entry["board"]
        display(Markdown(f"## Tablero {idx+1}/{len(entries)}"))
        arr = np.array(board, dtype=np.uint8)
        img = Image.fromarray(arr).resize((N*30, N*30), Image.NEAREST)
        display(img)
        
        # 2) Calculamos y mostramos la secuencia de resolución
        display(Markdown("**Secuencia completa de resolución:**"))
        steps = record_resolution_steps(board)
        if not steps:
            display(Markdown("_No se aplicó ninguna regla (tablero trivial)._"))
        else:
            for i, rule_name in enumerate(steps, start=1):
                display(Markdown(f"{i}. {rule_name}"))


# %%
import ipywidgets as widgets
from IPython.display import display, Markdown, clear_output

# --------------------------------------------------------------------------------
# 1) Función auxiliar para mostrar base (step=0) o overlay (step>0)
def overlay_for_step(board_idx: int, step_idx: int):
    """
    Si step_idx == 0 devuelve la imagen base coloreada,
    si step_idx > 0 llama a draw_overlay con step_idx-1.
    """
    if step_idx == 0:
        # Tablero base sin overlay
        board = entries[board_idx]["board"]
        img = Image.fromarray(
            np.array(board, dtype=np.uint8)
        ).resize((N*30, N*30), Image.NEAREST)
        return img
    else:
        # Overlay acumulado hasta sub-paso step_idx-1
        return draw_overlay(board_idx, step_idx - 1)

# --------------------------------------------------------------------------------
# 2) Creamos los sliders
board_slider = widgets.IntSlider(
    value=0,
    min=0,
    max=len(entries)-1,
    step=1,
    description='Tablero:',
    continuous_update=False
)
step_slider = widgets.IntSlider(
    value=0,
    min=0,
    max=len(entries_changes[0]),  # se ajustará dinámicamente
    step=1,
    description='Paso:',
    continuous_update=False
)

# 3) Salida única
out = widgets.Output()

# --------------------------------------------------------------------------------
# 4) Función de actualización que lee ambos sliders
def update(_=None):
    b = board_slider.value
    s = step_slider.value

    # Ajustar rango de step_slider al cambiar de tablero
    max_step = len(entries_changes[b])
    step_slider.max = max_step

    with out:
        clear_output(wait=True)
        # Etiqueta descriptiva
        if s == 0:
            label = "Estado inicial (sin pasos aplicados)"
        else:
            lbl = entries_changes[b][s-1]["label"]
            label = f"Paso {s}: {lbl}"
        display(Markdown(f"## Tablero {b+1}/{len(entries)} — {label}"))
        # Imagen con overlay_for_step
        img = overlay_for_step(b, s)
        display(img)

# --------------------------------------------------------------------------------
# 5) Conectar observadores y mostrar UI
board_slider.observe(update, names='value')
step_slider.observe(update, names='value')

ui = widgets.VBox([board_slider, step_slider])
display(ui, out)

# 6) Render inicial
update()


# %%
# step1(): Deducción por color único
# Si un color solo aparece como candidato en una posición, se coloca una reina allí.

# step2(): Deducción por fila
# Si una fila tiene solo un candidato válido, se coloca una reina allí.

# step3(): Eliminación por uniformidad
# Si una fila o columna tiene todas las celdas del mismo color, se eliminan candidatos de ese color en otras filas/columnas.

# step4(): Naked sets
# Busca subconjuntos de colores que están restringidos a subconjuntos equivalentes de filas/columnas. Si el tamaño del conjunto de colores es igual al número de filas/columnas donde aparecen, se eliminan candidatos fuera de ese subconjunto.

# step5_and_6(): Seguridad global
# Simula colocar cada reina candidata y elimina aquellas que:

print(record_resolution_steps(board))



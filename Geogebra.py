import sys
import matplotlib
if sys.platform.startswith('linux'):
    try:
        matplotlib.use('TkAgg')
    except ImportError:
        pass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
import tkinter as tk
from tkinter import simpledialog

# ==========================================
# 1. ENTRADAS DINÁMICAS (Ventana tkinter)
# ==========================================
root = tk.Tk()
root.withdraw()

funcion_texto = simpledialog.askstring("GeoGebra de Riemann", "Ingresa f(x):", initialvalue="-x**2 + 4")
if not funcion_texto or not funcion_texto.strip():
    funcion_texto = "-x**2 + 4"

str_a = simpledialog.askstring("GeoGebra de Riemann", "Límite inferior 'a':", initialvalue="-2")
a = eval(str_a) if str_a and str_a.strip() else -2

str_b = simpledialog.askstring("GeoGebra de Riemann", "Límite superior 'b':", initialvalue="2")
b = eval(str_b) if str_b and str_b.strip() else 2

root.destroy()

# ==========================================
# 2. LÓGICA Y GRÁFICA (sin cambios)
# ==========================================
def f(x):
    return eval(funcion_texto)

n_inicial = 4

fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.25)

x_curva = np.linspace(a - 0.5, b + 0.5, 1000)
y_curva = f(x_curva)

def calcular_y_dibujar(n_actual):
    ax.clear()
    delta_x = (b - a) / n_actual
    area_total = 0
    lista_ci = []
    lista_alturas = []
    lista_x_izq = []  # nueva lista

    for i in range(int(n_actual)):
        x_izq = a + i * delta_x
        c_i = x_izq + 0.5 * delta_x  # punto medio
        altura = f(c_i)
        area_total += altura * delta_x
        lista_ci.append(c_i)
        lista_alturas.append(altura)
        lista_x_izq.append(x_izq)  # guardar extremo izquierdo

    ax.plot(x_curva, y_curva, color='blue', linewidth=2, label=f'$f(x) = {funcion_texto}$')
    ax.bar(lista_x_izq, lista_alturas, width=delta_x, align='edge',  # usar x_izq aquí
           alpha=0.5, color='orange', edgecolor='darkorange', label='Rectángulos de Riemann')
    ax.scatter(lista_ci, lista_alturas, color='red', zorder=5, s=15)
    ax.axhline(0, color='black', linewidth=1.2)
    ax.axvline(0, color='black', linewidth=1.2)
    ax.set_title(f'Función: {funcion_texto}\nIntervalos (n) = {int(n_actual)} | Área aprox = {area_total:.4f}', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')
    ax.set_ylim(min(y_curva) - 1, max(y_curva) + 1)

calcular_y_dibujar(n_inicial)

# ==========================================
# 3. DESLIZADOR
# ==========================================
ax_slider = plt.axes([0.15, 0.1, 0.7, 0.03])
slider_n = Slider(ax=ax_slider, label='Intervalos (n) ', valmin=1, valmax=100,
                  valinit=n_inicial, valfmt='%d', color='skyblue')

def actualizar(val):
    calcular_y_dibujar(slider_n.val)
    fig.canvas.draw_idle()

slider_n.on_changed(actualizar)
plt.show()
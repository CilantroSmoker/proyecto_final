import sys
import matplotlib
if sys.platform.startswith('linux'):
    try: matplotlib.use('TkAgg')
    except ImportError: pass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, TextBox

# ==========================================
# 1. VALORES INICIALES POR DEFECTO
# ==========================================
funcion_inicial = "np.sin(x) + np.cos(y) + 2" # Arrancamos directo con las olas
x_min, x_max = -1.5, 1.5
y_min, y_max = -1.5, 1.5
n_inicial = 4

# CONFIGURACIÓN DE LA VENTANA
fig = plt.figure(figsize=(11, 8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.35)

# ==========================================
# 2. EVALUADOR REMASTERIZADO Y BLINDADO
# ==========================================
def evaluar_funcion_3d(x_array, y_array, texto_funcion):
    """Evalúa funciones matemáticas sobre matrices evitando errores de tipo."""
    # Diccionario con las funciones matemáticas para que eval las reconozca directamente
    contexto = {
        "x": x_array, 
        "y": y_array, 
        "np": np,
        "sin": np.sin,
        "cos": np.cos,
        "sqrt": np.sqrt,
        "exp": np.exp,
        "pi": np.pi
    }
    try:
        # Limpiamos el texto por si acaso el usuario escribe "np.np.sin" por error
        txt = texto_funcion.replace("np.", "")
        
        # Evaluamos usando el entorno controlado
        resultado = eval(txt, {"__builtins__": None}, contexto)
        
        # Convertimos de forma segura a un arreglo numérico de NumPy
        return np.asarray(resultado, dtype=float)
    except Exception as e:
        # Si hay un error mientras el usuario teclea, muestra una matriz plana en 0
        return np.zeros_like(x_array, dtype=float)

# ==========================================
# 3. FUNCIÓN DE RENDERIZADO PRINCIPAL
# ==========================================
def dibujar_3d(n_val, texto_funcion):
    ax.clear()
    n_val = int(n_val)
    
    # 1. Muestreo suave para la malla translúcida de fondo
    X_mesh, Y_mesh = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
    Z_mesh = evaluar_funcion_3d(X_mesh, Y_mesh, texto_funcion)
    
    # Dibujar la superficie de fondo
    ax.plot_surface(X_mesh, Y_mesh, Z_mesh, alpha=0.25, cmap='coolwarm', edgecolor='none')
    
    # 2. Geometría de los prismas de Riemann (Legos)
    dx = (x_max - x_min) / n_val
    dy = (y_max - y_min) / n_val
    
    x_pos, y_pos = np.meshgrid(np.linspace(x_min, x_max - dx, n_val), np.linspace(y_min, y_max - dy, n_val))
    x_pos = x_pos.ravel()
    y_pos = y_pos.ravel()
    z_pos = np.zeros_like(x_pos)
    
    # Evaluar alturas en el punto medio exacto de cada prisma
    alturas = evaluar_funcion_3d(x_pos + dx/2, y_pos + dy/2, texto_funcion)
    alturas = np.nan_to_num(alturas, nan=0.0) 
    
    # Dimensiones de las columnas
    bars_dx = np.ones_like(x_pos) * dx
    bars_dy = np.ones_like(y_pos) * dy
    
    # Dibujar los prismas 3D
    ax.bar3d(x_pos, y_pos, z_pos, bars_dx, bars_dy, alturas, 
             color='orange', alpha=0.5, edgecolor='darkorange')
    
    # Calcular volumen aproximado de la suma de Riemann 3D
    volumen = np.sum(alturas * dx * dy)
    
    ax.set_title(f'Suma de Riemann 3D (Volumen)\nBloques: {n_val}x{n_val} | Vol aprox = {volumen:.4f}', fontsize=12)
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_zlabel('Eje Z (Alturas)')
    
    # Auto-ajuste inteligente del eje Z
    max_h = np.max(alturas) if len(alturas) > 0 else 0
    max_m = np.max(Z_mesh) if len(Z_mesh) > 0 else 0
    lim_superior = max(max_h, max_m)
    
    if lim_superior > 0:
        ax.set_zlim(0, lim_superior * 1.2)
    else:
        ax.set_zlim(0, 5)

# ==========================================
# 4. INTERFAZ EN VIVO (CONTROLES)
# ==========================================
ax_box_f = plt.axes([0.2, 0.20, 0.6, 0.04])
text_box_f = TextBox(ax=ax_box_f, label='f(x, y) = ', initial=funcion_inicial)

ax_slider = plt.axes([0.2, 0.10, 0.6, 0.03])
slider_n = Slider(ax=ax_slider, label='Cuadrícula (N) ', valmin=2, valmax=25, valinit=n_inicial, valfmt='%d', color='skyblue')

def actualizar_todo(val_o_texto_ignorado):
    dibujar_3d(slider_n.val, text_box_f.text)
    fig.canvas.draw_idle()

slider_n.on_changed(actualizar_todo)
text_box_f.on_submit(actualizar_todo)

# Primera ejecución en el arranque
dibujar_3d(n_inicial, funcion_inicial)
plt.show()
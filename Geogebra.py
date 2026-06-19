import matplotlib
matplotlib.use('TkAgg')  # <--- Esto le dice a Python: "¡Usa ventanas interactivas!"
import matplotlib.pyplot as plt
import numpy as np


# 1. Definición de la función y datos
def f(x):
    return -x**2 + 4

a = -2
b = 2
n = 4
delta_x = (b - a) / n

# Listas para guardar los datos que vamos a graficar
lista_ci = []
lista_alturas = []
area_total = 0

# 2. El bucle matemático (igual al tuyo)
for i in range(n):
    c_i = a + i * delta_x
    altura = f(c_i)
    area_rectangulo = altura * delta_x
    area_total += area_rectangulo
    
    # Guardamos los puntos para el gráfico
    lista_ci.append(c_i)
    lista_alturas.append(altura)

print(f"El área aproximada es: {area_total}")

# ==========================================
# 3. BLOQUE DE GRÁFICO (Estilo GeoGebra)
# ==========================================

# Generamos puntos continuos para dibujar la curva suave de la función
x_curva = np.linspace(a - 1, b + 1, 1000)
y_curva = f(x_curva)

# Crear la figura
plt.figure(figsize=(10, 6))

# Dibujar la curva de la función en azul
plt.plot(x_curva, y_curva, color='blue', linewidth=2, label=f'$f(x) = x^2 - 4x$')

# Dibujar los rectángulos de Riemann
# 'align="edge"' hace que el rectángulo empiece en C_i (extremo izquierdo)
plt.bar(lista_ci, lista_alturas, width=delta_x, align='edge', 
        alpha=0.4, color='orange', edgecolor='darkorange', label='Rectángulos de Riemann')

# Dibujar los puntos C_i sobre la curva
plt.scatter(lista_ci, lista_alturas, color='red', zorder=5, label='Representantes ($C_i$)')

# Configuración y estética del gráfico
plt.axhline(0, color='black', linewidth=1.2) # Eje X
plt.axvline(0, color='black', linewidth=1.2) # Eje Y
plt.title(f'Suma de Riemann (Izquierda) - Área aprox: {area_total}', fontsize=14)
plt.xlabel('Eje X')
plt.ylabel('Eje Y')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# Mostrar la ventana con el gráfico interactivo
plt.show()
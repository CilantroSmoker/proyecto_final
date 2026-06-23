import sys
import matplotlib

if sys.platform.startswith('linux'):
    try:
        matplotlib.use('TkAgg')
    except ImportError:
        pass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, TextBox, RadioButtons
import scipy.integrate as integrate


f_inicial = "-x**2 + 4"
g_inicial = "0"          # Por defecto es cero (área contra el piso)
a_actual = -2.0
b_actual = 2.0
n_inicial = 4
metodo_inicial = "Punto Medio"
modo_inicial = "Área"    # Puede ser "Área" o "Longitud"


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), gridspec_kw={'width_ratios': [2, 1]})
plt.subplots_adjust(bottom=0.38, left=0.22, wspace=0.25)  

def calcular_y_dibujar(n_val, f_txt, g_txt, a_val, b_val, metodo, modo):
    ax1.clear()
    ax2.clear()
    
    try:
        # Funciones base seguras y vectorizadas para NumPy 2.0
        def evaluar_f(x, txt):
            contexto = {"x": x, "np": np}
            try:
                val = eval(txt, {}, contexto)
                if isinstance(val, np.ndarray): return val.astype(float)
                return float(val)
            except:
                return 0.0

        f = np.vectorize(lambda x: evaluar_f(x, f_txt), otypes=[float])
        g = np.vectorize(lambda x: evaluar_f(x, g_txt), otypes=[float])
        
        # Muestreo para curvas continuas
        x_curva = np.linspace(a_val - 0.5, b_val + 0.5, 1000)
        y_f = np.nan_to_num(f(x_curva), nan=0.0)
        y_g = np.nan_to_num(g(x_curva), nan=0.0)
        
        delta_x = (b_val - a_val) / n_val
        
        # Dibujar las dos curvas principales si g(x) no es cero
        ax1.plot(x_curva, y_f, color='blue', linewidth=2, label=f'$f(x) = {f_txt}$')
        if g_txt.strip() != "0":
            ax1.plot(x_curva, y_g, color='purple', linewidth=1.5, linestyle='--', label=f'$g(x) = {g_txt}$')

        
        if modo == "Área":
            area_aproximada = 0
            lista_x_izq, lista_alturas, lista_bases, lista_ci = [], [], [], []
            
            for i in range(int(n_val)):
                x_izq = a_val + i * delta_x
                x_der = x_izq + delta_x
                
                if metodo == "Izquierda": c_i = x_izq
                elif metodo == "Derecha": c_i = x_der
                elif metodo == "Punto Medio": c_i = x_izq + 0.5 * delta_x
                
                if metodo == "Trapecios":
                    h_f_izq, h_g_izq = f(x_izq), g(x_izq)
                    h_f_der, h_g_der = f(x_der), g(x_der)
                    # Altura neta del trapecio flotante
                    area_aproximada += (((h_f_izq - h_g_izq) + (h_f_der - h_g_der)) / 2) * delta_x
                    ax1.fill([x_izq, x_der, x_der, x_izq], [h_g_izq, h_g_der, h_f_der, h_f_izq], 
                             facecolor='orange', edgecolor='darkorange', alpha=0.4)
                else:
                    alt_f = f(c_i)
                    alt_g = g(c_i)
                    altura_neta = alt_f - alt_g
                    area_aproximada += altura_neta * delta_x
                    
                    lista_x_izq.append(x_izq)
                    lista_alturas.append(altura_neta)
                    lista_bases.append(alt_g) # La base del rectángulo se apoya en g(x)
                    lista_ci.append(c_i)
            
            if metodo != "Trapecios":
                # Dibujamos las barras flotantes (bottom=lista_bases hace la magia)
                ax1.bar(lista_x_izq, lista_alturas, width=delta_x, bottom=lista_bases, align='edge', 
                       alpha=0.5, color='orange', edgecolor='darkorange', label=f'Suma ({metodo})')
                ax1.scatter(lista_ci, f(lista_ci), color='red', zorder=5, s=15)
            else:
                ax1.fill_between([], [], color='orange', alpha=0.5, edgecolor='darkorange', label='Trapecios')
                
            # Integral Exacta del Área usando SciPy
            integral_real, _ = integrate.quad(lambda x: f(x) - g(x), a_val, b_val)
            error_absoluto = abs(integral_real - area_aproximada)
            
            ax1.set_title(f'Visualización del Área\nAprox: {area_aproximada:.6f} | Real: {integral_real:.6f}', fontsize=10)

        
        else: 
            # Aproximamos la longitud uniendo puntos sobre f(x) con diagonales (Pitágoras)
            x_puntos = np.linspace(a_val, b_val, int(n_val) + 1)
            y_puntos = f(x_puntos)
            
            longitud_aproximada = 0
            for i in range(len(x_puntos) - 1):
                x1, x2 = x_puntos[i], x_puntos[i+1]
                y1, y2 = y_puntos[i], y_puntos[i+1]
                # Distancia diagonal del segmento
                dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                longitud_aproximada += dist
                # Dibujamos el segmento de recta sobre la curva
                ax1.plot([x1, x2], [y1, y2], color='darkorange', linewidth=2.5, marker='o', markersize=4)
                
            ax1.plot([], [], color='darkorange', label='Segmentos de Línea') # Para la leyenda
            
            # Integral exacta de la longitud de arco usando la derivada numérica
            def f_linea(x):
                h = 1e-5
                derivada = (f(x + h) - f(x - h)) / (2 * h)
                return np.sqrt(1 + derivada**2)
                
            integral_real, _ = integrate.quad(f_linea, a_val, b_val)
            error_absoluto = abs(integral_real - longitud_aproximada)
            
            ax1.set_title(f'Longitud de la Curva f(x)\nAprox: {longitud_aproximada:.6f} | Real: {integral_real:.6f}', fontsize=10)

        # --- FILTRO INTELIGENTE DE ZOOM VERTICAL ---
        y_combinado = np.concatenate([y_f, y_g])
        y_filtrado = y_combinado[(y_combinado > -1e5) & (y_combinado < 1e5)]
        min_y = max(min(y_filtrado) - 1, -10)
        max_y = min(max(y_filtrado) + 1, 10)
        ax1.set_ylim(min_y, max_y)

        ax1.axhline(0, color='black', linewidth=1)
        ax1.axvline(0, color='black', linewidth=1)
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.legend(loc='upper right')

        # --- CURVA DE CONVERGENCIA ---
        pasos_n = np.unique(np.linspace(1, int(n_val), num=min(int(n_val), 30), dtype=int))
        errores = []
        
        for n_pasa in pasos_n:
            dx_pasa = (b_val - a_val) / n_pasa
            if modo == "Área":
                aprox_pasa = 0
                for k in range(n_pasa):
                    xi = a_val + k * dx_pasa
                    if metodo == "Izquierda": c = xi
                    elif metodo == "Derecha": c = xi + dx_pasa
                    elif metodo == "Punto Medio": c = xi + 0.5 * dx_pasa
                    
                    if metodo == "Trapecios":
                        aprox_pasa += (((f(xi)-g(xi)) + (f(xi+dx_pasa)-g(xi+dx_pasa))) / 2) * dx_pasa
                    else:
                        aprox_pasa += (f(c) - g(c)) * dx_pasa
                errores.append(abs(integral_real - aprox_pasa))
            else:
                long_pasa = 0
                xp = np.linspace(a_val, b_val, n_pasa + 1)
                yp = f(xp)
                for k in range(len(xp) - 1):
                    long_pasa += np.sqrt((xp[k+1] - xp[k])**2 + (yp[k+1] - yp[k])**2)
                errores.append(abs(integral_real - long_pasa))
            
        ax2.plot(pasos_n, errores, color='red', marker='o', markersize=4, linestyle='-', linewidth=1.5)
        ax2.set_title(f'Curva de Convergencia\nError Absoluto: {error_absoluto:.6f}', fontsize=10, color='darkred')
        ax2.set_xlabel('Número de Intervalos (n)')
        ax2.set_ylabel('Error Absoluto')
        ax2.grid(True, linestyle='--', alpha=0.5)

    except Exception as e:
        ax1.set_title(f"Error: {e}", color="red", fontsize=12)

ax_slider = plt.axes([0.25, 0.28, 0.6, 0.03])
slider_n = Slider(ax=ax_slider, label='Intervalos (n) ', valmin=1, valmax=100, valinit=n_inicial, valfmt='%d', color='skyblue')

ax_box_f = plt.axes([0.25, 0.20, 0.6, 0.04])
text_box_f = TextBox(ax=ax_box_f, label='f(x) = ', initial=f_inicial)

ax_box_g = plt.axes([0.25, 0.13, 0.6, 0.04])
text_box_g = TextBox(ax=ax_box_g, label='g(x) = ', initial=g_inicial)

ax_box_a = plt.axes([0.25, 0.05, 0.2, 0.04])
text_box_a = TextBox(ax=ax_box_a, label='Límite a = ', initial=str(a_actual))

ax_box_b = plt.axes([0.65, 0.05, 0.2, 0.04])
text_box_b = TextBox(ax=ax_box_b, label='Límite b = ', initial=str(b_actual))

# Selector de Métodos (Izquierda, Derecha...)
ax_radio_metodos = plt.axes([0.02, 0.52, 0.15, 0.18])
radio_metodos = RadioButtons(ax_radio_metodos, ('Izquierda', 'Derecha', 'Punto Medio', 'Trapecios'), active=2, activecolor='darkorange')

# NUEVO: Selector de Modo (Área vs Longitud)
ax_radio_modo = plt.axes([0.02, 0.28, 0.15, 0.12])
radio_modo = RadioButtons(ax_radio_modo, ('Área', 'Longitud de Línea'), active=0, activecolor='blue')

def actualizar_todo(val_o_text_ignorado):
    n_val = slider_n.val
    f_txt = text_box_f.text
    g_txt = text_box_g.text
    metodo = radio_metodos.value_selected
    modo = radio_modo.value_selected
    try:
        a_val = eval(text_box_a.text)
        b_val = eval(text_box_b.text)
    except:
        a_val, b_val = -2.0, 2.0
        
    calcular_y_dibujar(n_val, f_txt, g_txt, a_val, b_val, metodo, modo)
    fig.canvas.draw_idle()

slider_n.on_changed(actualizar_todo)
text_box_f.on_submit(actualizar_todo)
text_box_g.on_submit(actualizar_todo)
text_box_a.on_submit(actualizar_todo)
text_box_b.on_submit(actualizar_todo)
radio_metodos.on_clicked(actualizar_todo)
radio_modo.on_clicked(actualizar_todo)

calcular_y_dibujar(n_inicial, f_inicial, g_inicial, a_actual, b_actual, metodo_inicial, modo_inicial)
plt.show()
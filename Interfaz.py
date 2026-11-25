import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

import asistencia as herpo  # Tu archivo con las reglas y funciones del sistema


#  INTERFAZ GRÁFICA - SISTEMA DE ASISTENCIA HERPO
#  Archivos utilizados:
#- asistencia.py 
#- logo_herpo.png

# Para que los archivos .txt y el logo se busquen junto a este archivo
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Colores y fuentes
COLOR_FONDO = "#3A3A3A"        # Gris oscuro
COLOR_BOTON = "#0094C8"        # Azul Herpo
COLOR_BOTON_ACTIVO = "#007AA6" # Azul un poco más oscuro al presionar
COLOR_TEXTO = "white"
COLOR_SUBTITULO = "#AAAAAA"

FUENTE_BOTON = ("Arial", 11, "bold")
FUENTE_TEXTO = ("Arial", 10)
FUENTE_TITULO = ("Arial", 14, "bold")

#Ventana principal
ventana = tk.Tk()
ventana.title("Sistema de asistencia - Herpo")
ventana.geometry("480x760")
ventana.configure(bg=COLOR_FONDO)
ventana.resizable(False, False)

# Se carga el logo; si no se encuentra, se muestra solo el nombre
try:
    logo = tk.PhotoImage(file="logo_herpo.png")
except tk.TclError:
    logo = None


#  SECCIÓN FUNCIONES DE APOYO
#  Hacen lo mismo que las opciones de consola de tu archivo,
#  pero reciben los datos como parámetros (en vez de input())
#  y devuelven texto (en vez de print()). Usan tus funciones
#  y tus reglas a través de "herpo".

# 1. Para obtener el nombre completo de un trabajador
def nombre_completo(codigo):
    """Devuelve 'Nombre Apellido' del código, o '' si no existe."""
    for nombre, apellido, cod in herpo.leer_trabajadores():
        if cod == codigo:
            return f"{nombre} {apellido}"
    return ""

# 2. Para convertir un texto en fecha
def convertir_fecha(texto):
    """Convierte 'AAAA-MM-DD' en datetime. Devuelve None si el formato es incorrecto."""
    try:
        return datetime.strptime(texto.strip(), herpo.FORMATO_FECHA)
    except ValueError:
        return None

# 3. Para validar y guardar un trabajador nuevo (igual a registrar_trabajador)
def guardar_trabajador(nombre, apellido, codigo):
    """Valida y guarda un trabajador. Devuelve un mensaje de error, o '' si todo salió bien."""
    if not nombre or not apellido or not codigo:
        return "Todos los campos son obligatorios."
    if not herpo.texto_valido(nombre) or not herpo.texto_valido(apellido):
        return "El nombre y el apellido solo pueden tener letras y espacios."
    if len(codigo) != 4:
        return "El código debe tener exactamente 4 dígitos."
    if not codigo.isdigit():
        return "El código debe contener solo números."
    if herpo.codigo_registrado(codigo):
        return "Ya existe un trabajador con este código."

    with open(herpo.trabajadores, "a", encoding="utf-8") as f:
        f.write(f"{nombre},{apellido},{codigo}\n")
    return ""

# 4. Para validar y guardar un ingreso o una salida (igual a marcar_actividad)
def guardar_marcacion(tipo, codigo):
    """
    Guarda un ingreso o una salida con la fecha y hora actuales.
    Devuelve (error, fecha_hora): si todo salió bien, error es ''.
    """
    if not herpo.codigo_valido(codigo):
        return "Ingrese un código válido de exactamente 4 números.", ""
    if not herpo.codigo_registrado(codigo):
        return "El código no está registrado.", ""

    ahora = datetime.now()
    hoy = ahora.strftime(herpo.FORMATO_FECHA)

    # Se permite una sola jornada (un ingreso y una salida) por día
    ingresos_hoy = herpo.agrupar_por_dia(herpo.leer_marcaciones(herpo.ingresos, codigo)).get(hoy, [])
    salidas_hoy = herpo.agrupar_por_dia(herpo.leer_marcaciones(herpo.salidas, codigo)).get(hoy, [])

    if tipo == "ingreso" and ingresos_hoy:
        return "Este trabajador ya marcó su ingreso hoy.", ""
    if tipo == "salida" and not ingresos_hoy:
        return "No se puede marcar salida sin haber marcado ingreso hoy.", ""
    if tipo == "salida" and salidas_hoy:
        return "Este trabajador ya marcó su salida hoy.", ""

    fecha_hora = ahora.strftime(herpo.FORMATO_FECHA_HORA)
    if tipo == "ingreso":
        archivo = herpo.ingresos
    else:
        archivo = herpo.salidas

    with open(archivo, "a", encoding="utf-8") as f:
        f.write(f"{codigo},{fecha_hora}\n")
    return "", fecha_hora

# 5. Para armar el texto de ingresos y salidas (igual a consultar_por_codigo)
def texto_actividad(codigo):
    """Devuelve un texto con todos los ingresos y salidas de un código."""
    lista_ingresos = herpo.leer_marcaciones(herpo.ingresos, codigo)
    lista_salidas = herpo.leer_marcaciones(herpo.salidas, codigo)

    if not lista_ingresos and not lista_salidas:
        return "Sin registros de ingresos o salidas para este código."

    lineas = ["--- INGRESOS ---"]
    for momento in lista_ingresos:
        lineas.append(momento.strftime(herpo.FORMATO_FECHA_HORA))
    lineas.append("")
    lineas.append("--- SALIDAS ---")
    for momento in lista_salidas:
        lineas.append(momento.strftime(herpo.FORMATO_FECHA_HORA))
    return "\n".join(lineas)

# 6. Para armar el texto con la lista de trabajadores (igual a listar_trabajadores)
def texto_lista_trabajadores():
    """Devuelve un texto con todos los trabajadores registrados."""
    lista = herpo.leer_trabajadores()
    if not lista:
        return "Aún no hay trabajadores registrados."
    lineas = []
    for nombre, apellido, codigo in lista:
        lineas.append(f"{codigo} - {nombre} {apellido}")
    return "\n".join(lineas)

# 7. Para armar el texto del reporte (igual a calcular_reporte_horas + imprimir_resumen)
def texto_reporte(codigo, desde, hasta):
    """Devuelve el reporte de horas y sanciones de un trabajador como texto."""
    resumen = herpo.calcular_resumen(codigo, desde, hasta)

    if not resumen["detalle"]:
        return "No hay marcaciones ni faltas en el rango indicado."

    lineas = [f"Resumen de {nombre_completo(codigo)} ({codigo}):", "-" * 46]

    for dia in resumen["detalle"]:
        lineas.append(f"Fecha: {dia['fecha']}")
        lineas.append(f"  • Horas que debía cumplir: {dia['horas_a_cumplir']:.2f} hrs")
        if dia["estado"] == "COMPLETA":
            lineas.append(f"  • Horas normales (antes de las {herpo.HORA_EXTRA}:00): {dia['horas_normales']:.2f} hrs")
            lineas.append(f"  • Horas extra (después de las {herpo.HORA_EXTRA}:00): {dia['horas_extra']:.2f} hrs")
        else:
            lineas.append(f"  ALERTA / SANCIÓN: {dia['estado']}")

        if dia["saldo"] > 0:
            lineas.append(f"  [!] Debe {dia['saldo']:.2f} hrs: se suman a la jornada de mañana.")
        elif dia["saldo"] < 0:
            lineas.append(f"  [+] Tiene {-dia['saldo']:.2f} hrs a favor: se restan de la jornada de mañana.")
        lineas.append("-" * 46)

    horas_proxima = max(0, herpo.JORNADA_BASE + resumen["saldo_final"])
    lineas.append(f"Horas extra (se pagan): {resumen['total_extra']:.2f} hrs")
    lineas.append(f"Total de sanciones: {resumen['sanciones']}")
    lineas.append(f"Horas a cumplir en su próxima jornada: {horas_proxima:.2f} hrs")
    return "\n".join(lineas)

# 8. Para calcular y exportar la nómina (igual a generar_nomina)
def exportar_nomina(desde, hasta):
    """
    Calcula la nómina de todos los trabajadores y la guarda en Nomina_H.csv.
    Devuelve una lista de textos (uno por trabajador) para mostrar en pantalla.
    Puede lanzar PermissionError si el archivo está abierto en Excel.
    """
    encabezado = ["Código", "Nombre", "Apellido", "Desde", "Hasta",
                  f"Horas extra (después de las {herpo.HORA_EXTRA}:00)", "Valor hora extra",
                  "Pago por horas extra", "Sanciones", "Saldo de horas (+ debe / - a favor)",
                  "Horas a cumplir próxima jornada"]

    lineas = [f"Valor de la hora extra: ${herpo.VALOR_HORA_EXTRA:,.0f}", "-" * 46]

    with open(herpo.nomina_csv, "w", encoding="utf-8-sig") as f:
        f.write(";".join(encabezado) + "\n")

        for nombre, apellido, codigo in herpo.leer_trabajadores():
            resumen = herpo.calcular_resumen(codigo, desde, hasta)
            pago_extra = resumen["total_extra"] * herpo.VALOR_HORA_EXTRA
            horas_proxima = max(0, herpo.JORNADA_BASE + resumen["saldo_final"])

            lineas.append(f"{codigo} - {nombre} {apellido}")
            lineas.append(f"  Horas extra: {resumen['total_extra']:.2f} | Pago: ${pago_extra:,.0f}")
            lineas.append(f"  Sanciones: {resumen['sanciones']} | Próxima jornada: {horas_proxima:.2f} hrs")

            fila = [codigo, nombre, apellido,
                    desde.strftime(herpo.FORMATO_FECHA), hasta.strftime(herpo.FORMATO_FECHA),
                    herpo.formato_excel(resumen["total_extra"]), str(herpo.VALOR_HORA_EXTRA),
                    herpo.formato_excel(pago_extra, 0), str(resumen["sanciones"]),
                    herpo.formato_excel(resumen["saldo_final"]), herpo.formato_excel(horas_proxima)]
            f.write(";".join(fila) + "\n")

    lineas.append("-" * 46)
    lineas.append(f"Nómina exportada al archivo: {herpo.nomina_csv}")
    return lineas

#SECCIÓN DE ELEMENTOS REUTILIZABLES DE LA INTERFAZ

# 9. Para limpiar la ventana y volver a poner el logo arriba (en todas las pantallas)
def limpiar_pantalla():
    for widget in ventana.winfo_children():
        widget.destroy()

    if logo is not None:
        tk.Label(ventana, image=logo, bg=COLOR_FONDO).pack(pady=(15, 0))
    else:
        tk.Label(ventana, text="Herpo", font=("Arial", 28, "bold"),
                 fg=COLOR_BOTON, bg=COLOR_FONDO).pack(pady=(15, 0))

    tk.Label(ventana, text="Sistema de asistencia", font=("Arial", 10, "bold"),
             fg=COLOR_SUBTITULO, bg=COLOR_FONDO).pack(pady=(0, 10))

# 10. Para crear un título de pantalla
def crear_titulo(texto):
    tk.Label(ventana, text=texto, font=FUENTE_TITULO,
             fg=COLOR_TEXTO, bg=COLOR_FONDO).pack(pady=(0, 5))


# 11. Para crear un botón con el estilo de Herpo
def crear_boton(texto, comando):
    boton = tk.Button(ventana, text=texto, command=comando, font=FUENTE_BOTON,
                      bg=COLOR_BOTON, fg=COLOR_TEXTO,
                      activebackground=COLOR_BOTON_ACTIVO, activeforeground=COLOR_TEXTO,
                      relief="flat", bd=0, cursor="hand2", width=30, pady=8)
    boton.pack(pady=6)

# 12. Para crear una etiqueta con su cuadro de texto
def crear_campo(texto):
    tk.Label(ventana, text=texto, font=FUENTE_TEXTO,
             fg=COLOR_TEXTO, bg=COLOR_FONDO).pack(pady=(8, 2))
    entrada = tk.Entry(ventana, font=FUENTE_TEXTO, width=34, justify="center")
    entrada.pack()
    return entrada

# 13. Para crear el área donde se muestran resultados (con barra de desplazamiento)
def crear_area_texto(alto):
    marco = tk.Frame(ventana, bg=COLOR_FONDO)
    marco.pack(pady=10)
    barra = tk.Scrollbar(marco)
    barra.pack(side="right", fill="y")
    area = tk.Text(marco, width=52, height=alto, font=("Courier", 9), wrap="word",
                   bg="#2B2B2B", fg=COLOR_TEXTO, yscrollcommand=barra.set, state="disabled")
    area.pack(side="left")
    barra.config(command=area.yview)
    return area


# 14. Para escribir un texto dentro del área de resultados
def mostrar_en_area(area, texto):
    area.config(state="normal")   # Se habilita para poder escribir
    area.delete("1.0", tk.END)
    area.insert(tk.END, texto)
    area.config(state="disabled")  # Se bloquea para que el usuario no lo edite

#SECCIÓN DE PANTALLAS
# 15. Pantalla principal (menú)
def mostrar_menu():
    limpiar_pantalla()
    crear_boton("Registrar empleado", mostrar_registro)
    crear_boton("Marcar ingreso por código", lambda: mostrar_marcacion("ingreso"))
    crear_boton("Marcar salida por código", lambda: mostrar_marcacion("salida"))
    crear_boton("Buscar por código", mostrar_busqueda)
    crear_boton("Cálculo nómina", mostrar_nomina)
    crear_boton("Salir", ventana.destroy)

# 16. Pantalla: registrar empleado
def mostrar_registro():
    limpiar_pantalla()
    crear_titulo("Registrar empleado")
    entrada_nombre = crear_campo("Nombre")
    entrada_apellido = crear_campo("Apellido")
    entrada_codigo = crear_campo("Código (primeros 4 dígitos de la cédula)")

    # Esta función se ejecuta cuando se presiona el botón "Guardar"
    def guardar():
        nombre = entrada_nombre.get().strip()
        apellido = entrada_apellido.get().strip()
        codigo = entrada_codigo.get().strip()

        error = guardar_trabajador(nombre, apellido, codigo)
        if error:
            messagebox.showerror("Error", error)
        else:
            messagebox.showinfo("Registro exitoso", f"{nombre} {apellido} fue registrado.")
            entrada_nombre.delete(0, tk.END)
            entrada_apellido.delete(0, tk.END)
            entrada_codigo.delete(0, tk.END)

    tk.Label(ventana, bg=COLOR_FONDO).pack()  # Espacio en blanco
    crear_boton("Guardar", guardar)
    crear_boton("Volver al menú", mostrar_menu)


# 17. Pantalla: marcar ingreso o salida
def mostrar_marcacion(tipo):
    limpiar_pantalla()
    crear_titulo(f"Marcar {tipo}")
    entrada_codigo = crear_campo("Código del trabajador (4 dígitos)")
    entrada_codigo.focus_set()

    # Esta función se ejecuta al presionar el botón (o la tecla Enter)
    def marcar():
        codigo = entrada_codigo.get().strip()

        error, fecha_hora = guardar_marcacion(tipo, codigo)
        if error:
            messagebox.showerror("Error", error)
        else:
            messagebox.showinfo(f"Marcación de {tipo} registrada",
                                f"{nombre_completo(codigo)}\n{fecha_hora}")
            entrada_codigo.delete(0, tk.END)

    entrada_codigo.bind("<Return>", lambda evento: marcar())

    tk.Label(ventana, bg=COLOR_FONDO).pack()  # Espacio en blanco
    crear_boton(f"Marcar {tipo}", marcar)
    crear_boton("Volver al menú", mostrar_menu)

# 18. Pantalla: buscar por código
def mostrar_busqueda():
    limpiar_pantalla()
    crear_titulo("Buscar por código")
    entrada_codigo = crear_campo("Código del trabajador")

    def buscar():
        codigo = entrada_codigo.get().strip()
        if not herpo.codigo_valido(codigo):
            messagebox.showerror("Error", "Ingrese un código válido de exactamente 4 números.")
        elif not herpo.codigo_registrado(codigo):
            messagebox.showerror("Error", "El código no está registrado.")
        else:
            texto = f"{nombre_completo(codigo)}\n\n{texto_actividad(codigo)}"
            mostrar_en_area(area, texto)  # "area" se crea más abajo, antes de hacer clic

    def ver_todos():
        mostrar_en_area(area, texto_lista_trabajadores())

    crear_boton("Buscar", buscar)
    crear_boton("Ver todos los trabajadores", ver_todos)
    area = crear_area_texto(10)
    crear_boton("Volver al menú", mostrar_menu)

# 19. Pantalla: cálculo de nómina y reporte de horas
def mostrar_nomina():
    limpiar_pantalla()
    crear_titulo("Cálculo nómina")
    entrada_desde = crear_campo("Fecha inicial (AAAA-MM-DD)")
    entrada_hasta = crear_campo("Fecha final (AAAA-MM-DD)")
    entrada_codigo = crear_campo("Código (solo para el reporte de un trabajador)")

    # Para leer y validar las dos fechas; devuelve (desde, hasta) o None
    def leer_fechas():
        desde = convertir_fecha(entrada_desde.get())
        hasta = convertir_fecha(entrada_hasta.get())
        if desde is None or hasta is None:
            messagebox.showerror("Error", "Escriba las fechas con el formato AAAA-MM-DD\n(ejemplo: 2026-11-30).")
            return None
        if hasta < desde:
            messagebox.showerror("Error", "La fecha final no puede ser anterior a la inicial.")
            return None
        return desde, hasta

    def reporte():
        rango = leer_fechas()
        if rango is None:
            return
        codigo = entrada_codigo.get().strip()
        if not herpo.codigo_valido(codigo):
            messagebox.showerror("Error", "Ingrese un código válido de exactamente 4 números.")
        elif not herpo.codigo_registrado(codigo):
            messagebox.showerror("Error", "El código no está registrado.")
        else:
            mostrar_en_area(area, texto_reporte(codigo, rango[0], rango[1]))

    def exportar():
        rango = leer_fechas()
        if rango is None:
            return
        if not herpo.leer_trabajadores():
            messagebox.showwarning("Sin trabajadores", "Aún no hay trabajadores registrados.")
            return
        try:
            lineas = exportar_nomina(rango[0], rango[1])
        except PermissionError:
            messagebox.showerror("Error", f"Cierre el archivo {herpo.nomina_csv} en Excel e intente de nuevo.")
            return
        mostrar_en_area(area, "\n".join(lineas))
        messagebox.showinfo("Nómina exportada", f"Se generó el archivo {herpo.nomina_csv}.\nPuede abrirlo con Excel.")

    crear_boton("Reporte del trabajador", reporte)
    crear_boton("Exportar nómina a Excel", exportar)
    area = crear_area_texto(8)
    crear_boton("Volver al menú", mostrar_menu)

#SECCIÓN DE INICIO DEL PROGRAMA
herpo.crear_archivos()
mostrar_menu()
ventana.mainloop()
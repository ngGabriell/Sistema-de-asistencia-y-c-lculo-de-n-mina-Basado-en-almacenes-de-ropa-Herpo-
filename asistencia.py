#Sistema de asistencia y control de horas laborales para trabajadores de HERPO
#Estudiante a cargo: Gabriel Calzada Carabalí

import os
from datetime import datetime, timedelta

#Archivos que utiliza el sistema
trabajadores = "Trabajadores_H.txt"
ingresos = "Ingresos_H.txt"
salidas = "Salidas_H.txt"
nomina_csv = "Nomina_H.csv"  # Archivo que se genera al exportar la nómina

#Reglas de Herpo (Organizadas todas aquí para poder modificarlas fácilmente si cambian en el futuro)
JORNADA_BASE = 6          # Horas de la jornada diaria
HORA_EXTRA = 19           # Desde las 7 pm (19:00) las horas se pagan como extra
VALOR_HORA_EXTRA = 14500  # Pesos por cada hora extra
DIAS_LABORALES = [0, 1, 2, 3, 4, 5]  # 0 = lunes ... 5 = sábado

FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M:%S"
FORMATO_FECHA = "%Y-%m-%d"

#   SECCIÓN ARCHIVOS, VALIDACIONES Y LECTURA DE DATOS
# 1. Para crear los archivos si no existen
def crear_archivos():
    """Crea los tres archivos de texto con su encabezado si aún no existen."""
    for archivo in [trabajadores, ingresos, salidas]:
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8") as f:
                if archivo == trabajadores:
                    f.write("Nombre,Apellido,Código\n")
                else:
                    f.write("Código,Fecha y hora\n")

#   SECCIÓN DE VALIDACIONES Y LECTURA DE DATOS
# 2. Para validar el formato de un código
def codigo_valido(codigo):
    """Devuelve True si el código tiene exactamente 4 dígitos numéricos."""
    return len(codigo) == 4 and codigo.isdigit()

# 3. Para validar nombres y apellidos
def texto_valido(texto):
    """Devuelve True si el texto solo tiene letras y espacios (sin comas ni números)."""
    return texto.replace(" ", "").isalpha()

# 4. Para verificar si un código ya está registrado
def codigo_registrado(codigo):
    """Devuelve True si el código existe en el archivo de trabajadores."""
    with open(trabajadores, "r", encoding="utf-8") as f:
        next(f, None)  # Saltar la línea de encabezados
        for line in f:
            datos = line.strip().split(",")
            if len(datos) == 3 and datos[2] == codigo:
                return True
    return False

# 5. Para obtener la lista de todos los trabajadores
def leer_trabajadores():
    """Devuelve una lista de tuplas (nombre, apellido, código)."""
    lista = []
    with open(trabajadores, "r", encoding="utf-8") as f:
        next(f, None)
        for line in f:
            datos = line.strip().split(",")
            if len(datos) == 3:
                lista.append((datos[0], datos[1], datos[2]))
    return lista

# 6. Para leer las marcaciones de un trabajador (ingresos o salidas)
def leer_marcaciones(archivo, codigo):
    """Devuelve una lista de datetime con las marcaciones de un código."""
    lista = []
    with open(archivo, "r", encoding="utf-8") as f:
        next(f, None)
        for line in f:
            datos = line.strip().split(",")
            if len(datos) == 2 and datos[0] == codigo:
                try:
                    lista.append(datetime.strptime(datos[1], FORMATO_FECHA_HORA))
                except ValueError:
                    pass  # Si la fecha está dañada, se ignora esa línea
    return lista

# 7. Para agrupar las marcaciones por día
def agrupar_por_dia(lista):
    """Convierte una lista de datetime en un diccionario {'YYYY-MM-DD': [datetime, ...]}."""
    dias = {}
    for momento in lista:
        fecha = momento.strftime(FORMATO_FECHA)
        if fecha not in dias:
            dias[fecha] = []
        dias[fecha].append(momento)
    return dias

# 8. Para pedir una fecha al usuario hasta que sea válida
def pedir_fecha(mensaje):
    """Pide una fecha con formato AAAA-MM-DD y la devuelve como datetime."""
    while True:
        texto = input(mensaje).strip()
        try:
            return datetime.strptime(texto, FORMATO_FECHA)
        except ValueError:
            print("Error: use el formato AAAA-MM-DD (ejemplo: 2026-11-30).")

# 9. Para pedir el rango de fechas a evaluar
def pedir_rango():
    """Pide fecha inicial y final. Devuelve (desde, hasta) o None si el rango es inválido."""
    desde = pedir_fecha("Fecha inicial (AAAA-MM-DD): ")
    hasta = pedir_fecha("Fecha final (AAAA-MM-DD): ")
    if hasta < desde:
        print("Error: la fecha final no puede ser anterior a la inicial.")
        return None
    return desde, hasta

#   SECCIÓN DE REGISTRO Y MARCACIÓN
# 10. Para registrar un trabajador por primera vez
def registrar_trabajador():
    print("\n===== REGISTRO DE TRABAJADOR =====")
    nombre = input("Nombre del trabajador: ").strip()
    apellido = input("Apellido del trabajador: ").strip()
    codigo = input("Código (primeros 4 dígitos de la cédula): ").strip()

    if not nombre or not apellido or not codigo:
        print("Error: todos los campos son obligatorios.")
        return
    if not texto_valido(nombre) or not texto_valido(apellido):
        print("Error: el nombre y el apellido solo pueden tener letras y espacios.")
        return
    if len(codigo) != 4:
        print("Error: el código debe tener exactamente 4 dígitos.")
        return
    if not codigo.isdigit():
        print("Error: el código debe contener solo números.")
        return
    if codigo_registrado(codigo):
        print("Error: ya existe un trabajador con este código.")
        return

    with open(trabajadores, "a", encoding="utf-8") as f:
        f.write(f"{nombre},{apellido},{codigo}\n")
    print("Trabajador registrado exitosamente.")

# 11. Para marcar ingreso o salida por código
def marcar_actividad(tipo):
    print(f"\n===== MARCAR {tipo.upper()} =====")
    codigo = input("Ingrese el código del trabajador: ").strip()

    if not codigo_valido(codigo):
        print("Error: ingrese un código válido de exactamente 4 números.")
        return
    if not codigo_registrado(codigo):
        print("Error: el código no está registrado.")
        return

    ahora = datetime.now()
    hoy = ahora.strftime(FORMATO_FECHA)

    # Se permite una sola jornada (un ingreso y una salida) por día
    ingresos_hoy = agrupar_por_dia(leer_marcaciones(ingresos, codigo)).get(hoy, [])
    salidas_hoy = agrupar_por_dia(leer_marcaciones(salidas, codigo)).get(hoy, [])

    if tipo == "ingreso" and ingresos_hoy:
        print("Error: este trabajador ya marcó su ingreso hoy.")
        return
    if tipo == "salida" and not ingresos_hoy:
        print("Error: no se puede marcar salida sin haber marcado ingreso hoy.")
        return
    if tipo == "salida" and salidas_hoy:
        print("Error: este trabajador ya marcó su salida hoy.")
        return

    fecha_hora = ahora.strftime(FORMATO_FECHA_HORA)
    if tipo == "ingreso":
        archivo = ingresos
    else:
        archivo = salidas

    with open(archivo, "a", encoding="utf-8") as f:
        f.write(f"{codigo},{fecha_hora}\n")

    print(f"Marcación de {tipo} registrada exitosamente para el código {codigo}.")
    print(f"Fecha y hora: {fecha_hora}")

#   SECCIÓN DE CONSULTAS
# 12. Para listar los trabajadores registrados
def listar_trabajadores():
    print("\n===== TRABAJADORES REGISTRADOS =====")
    lista = leer_trabajadores()
    if not lista:
        print("Aún no hay trabajadores registrados.")
        return
    for nombre, apellido, codigo in lista:
        print(f"{codigo} - {nombre} {apellido}")


# 13. Para consultar los ingresos y salidas por código
def consultar_por_codigo():
    print("\n===== CONSULTAR ACTIVIDAD =====")  # "Actividad" = ingresos y salidas del trabajador
    codigo = input("Ingrese el código del trabajador: ").strip()

    if not codigo_valido(codigo):
        print("Error: ingrese un código válido de exactamente 4 números.")
        return
    if not codigo_registrado(codigo):
        print("Error: el código no está registrado.")
        return

    lista_ingresos = leer_marcaciones(ingresos, codigo)
    lista_salidas = leer_marcaciones(salidas, codigo)

    print("\n--- INGRESOS ---")
    for momento in lista_ingresos:
        print(momento.strftime(FORMATO_FECHA_HORA))

    print("\n--- SALIDAS ---")
    for momento in lista_salidas:
        print(momento.strftime(FORMATO_FECHA_HORA))

    if not lista_ingresos and not lista_salidas:
        print("Sin registros de ingresos o salidas para este código.")



#   SECCIÓN DE CÁLCULO DE HORAS, SANCIONES Y NÓMINA
# 14. Para calcular las horas trabajadas después de las 7 pm
def horas_extra(ingreso, salida):
    """Devuelve las horas trabajadas después de la HORA_EXTRA (7 pm) ese día."""
    limite = ingreso.replace(hour=HORA_EXTRA, minute=0, second=0, microsecond=0)
    if salida <= limite:
        return 0.0
    inicio = max(ingreso, limite)
    return (salida - inicio).total_seconds() / 3600


# 15. Para calcular el resumen de un trabajador en un rango de fechas
def calcular_resumen(codigo, fecha_desde, fecha_hasta):
    """
    Recorre día por día el rango y devuelve un diccionario con:
      - detalle: lista con lo ocurrido en cada día evaluado
      - total_extra: horas trabajadas después de las 7 pm (se pagan)
      - sanciones: cantidad de faltas y marcaciones incompletas
      - saldo_final: horas pendientes (positivo = debe, negativo = a favor)

    El "saldo" es el ajuste que se arrastra al día siguiente:
      - Si trabajó más de lo que debía (antes de las 7 pm), le queda saldo a favor.
      - Si faltó o dejó la marcación incompleta, esas horas quedan como deuda.
    """
    dias_ingreso = agrupar_por_dia(leer_marcaciones(ingresos, codigo))
    dias_salida = agrupar_por_dia(leer_marcaciones(salidas, codigo))

    detalle = []
    total_extra = 0.0
    sanciones = 0
    saldo = 0.0  # Positivo = debe horas, negativo = tiene horas a favor

    dia = fecha_desde
    while dia <= fecha_hasta:
        fecha_str = dia.strftime(FORMATO_FECHA)
        hay_ingreso = fecha_str in dias_ingreso
        hay_salida = fecha_str in dias_salida

        # Horas que corresponden a este día (0 si no es día laboral)
        if dia.weekday() in DIAS_LABORALES:
            base = JORNADA_BASE
        else:
            base = 0

        estado = ""           # Queda vacío si no hay nada que reportar ese día
        horas_normales = 0.0
        extra = 0.0

        if not hay_ingreso and not hay_salida:
            if base > 0:
                estado = "FALTA"
        elif hay_ingreso and not hay_salida:
            estado = "SIN SALIDA"
        elif hay_salida and not hay_ingreso:
            estado = "SIN INGRESO"
        else:
            # Primer ingreso del día y última salida del día
            ingreso = min(dias_ingreso[fecha_str])
            salida = max(dias_salida[fecha_str])
            if salida <= ingreso:
                estado = "INCONSISTENTE"  # La salida es anterior al ingreso
            else:
                estado = "COMPLETA"
                horas_totales = (salida - ingreso).total_seconds() / 3600
                extra = horas_extra(ingreso, salida)
                horas_normales = horas_totales - extra

        if estado != "":
            horas_a_cumplir = max(0, base + saldo)
            # Lo que debía cumplir menos lo que trabajó (antes de las 7 pm)
            saldo = round(base + saldo - horas_normales, 2)

            if estado != "COMPLETA":
                sanciones += 1
            total_extra += extra

            detalle.append({
                "fecha": fecha_str,
                "estado": estado,
                "horas_a_cumplir": horas_a_cumplir,
                "horas_normales": horas_normales,
                "horas_extra": extra,
                "saldo": saldo,
            })

        dia += timedelta(days=1)

    return {
        "detalle": detalle,
        "total_extra": total_extra,
        "sanciones": sanciones,
        "saldo_final": saldo,
    }

# 16. Para mostrar el resumen en pantalla
def imprimir_resumen(resumen):
    print("-" * 50)
    for dia in resumen["detalle"]:
        print(f"Fecha: {dia['fecha']}")
        print(f"  • Horas que debía cumplir: {dia['horas_a_cumplir']:.2f} hrs")
        if dia["estado"] == "COMPLETA":
            print(f"  • Horas normales (antes de las {HORA_EXTRA}:00): {dia['horas_normales']:.2f} hrs")
            print(f"  • Horas extra (después de las {HORA_EXTRA}:00): {dia['horas_extra']:.2f} hrs")
        else:
            print(f"  ALERTA / SANCIÓN: {dia['estado']}")

        if dia["saldo"] > 0:
            print(f"  [!] Debe {dia['saldo']:.2f} hrs: se suman a la jornada de mañana.")
        elif dia["saldo"] < 0:
            print(f"  [+] Tiene {-dia['saldo']:.2f} hrs a favor: se restan de la jornada de mañana.")
        print("-" * 50)

# 17. Para calcular el reporte de horas y sanciones de un trabajador
def calcular_reporte_horas():
    print("\n===== REPORTE DE HORAS Y SANCIONES =====")
    codigo = input("Ingrese el código del trabajador a evaluar: ").strip()

    if not codigo_valido(codigo):
        print("Error: ingrese un código válido de exactamente 4 números.")
        return
    if not codigo_registrado(codigo):
        print("Error: el código no está registrado.")
        return

    rango = pedir_rango()
    if rango is None:
        return
    desde, hasta = rango

    resumen = calcular_resumen(codigo, desde, hasta)

    if not resumen["detalle"]:
        print("No hay marcaciones ni faltas en el rango indicado.")
        return

    print(f"\nResumen para el trabajador {codigo}:")
    imprimir_resumen(resumen)

    horas_proxima = max(0, JORNADA_BASE + resumen["saldo_final"])
    print(f"Horas extra (se pagan): {resumen['total_extra']:.2f} hrs")
    print(f"Total de sanciones: {resumen['sanciones']}")
    print(f"Horas que debe cumplir en su próxima jornada: {horas_proxima:.2f} hrs")

# 18. Para convertir un número a texto con coma decimal (así lo lee Excel en español)
def formato_excel(numero, decimales=2):
    return f"{numero:.{decimales}f}".replace(".", ",")

# 19. Para calcular la nómina de todos los trabajadores y exportarla a Excel
def generar_nomina():
    print("\n===== NÓMINA DEL PERIODO =====")
    lista = leer_trabajadores()
    if not lista:
        print("Aún no hay trabajadores registrados.")
        return

    rango = pedir_rango()
    if rango is None:
        return
    desde, hasta = rango

    encabezado = ["Código", "Nombre", "Apellido", "Desde", "Hasta",
                  f"Horas extra (después de las {HORA_EXTRA}:00)", "Valor hora extra",
                  "Pago por horas extra", "Sanciones", "Saldo de horas (+ debe / - a favor)",
                  "Horas a cumplir próxima jornada"]

    print(f"\nValor de la hora extra: ${VALOR_HORA_EXTRA:,.0f}")
    print("-" * 70)

    try:
        with open(nomina_csv, "w", encoding="utf-8-sig") as f:
            f.write(";".join(encabezado) + "\n")

            for nombre, apellido, codigo in lista:
                resumen = calcular_resumen(codigo, desde, hasta)
                pago_extra = resumen["total_extra"] * VALOR_HORA_EXTRA
                horas_proxima = max(0, JORNADA_BASE + resumen["saldo_final"])

                print(f"{codigo} - {nombre} {apellido}")
                print(f"  Horas extra: {resumen['total_extra']:.2f} | "
                      f"Pago: ${pago_extra:,.0f} | Sanciones: {resumen['sanciones']} | "
                      f"Próxima jornada: {horas_proxima:.2f} hrs")

                fila = [codigo, nombre, apellido,
                        desde.strftime(FORMATO_FECHA), hasta.strftime(FORMATO_FECHA),
                        formato_excel(resumen["total_extra"]), str(VALOR_HORA_EXTRA),
                        formato_excel(pago_extra, 0), str(resumen["sanciones"]),
                        formato_excel(resumen["saldo_final"]), formato_excel(horas_proxima)]
                f.write(";".join(fila) + "\n")
    except PermissionError:
        print(f"Error: cierre el archivo {nomina_csv} en Excel e intente de nuevo.")
        return

    print("-" * 70)
    print(f"Nómina exportada al archivo: {nomina_csv} (ábralo con Excel)")

#   SECCIÓN DE MENÚ PRINCIPAL (con las nuevas funciones agregadas)
# 20. Menú principal
def main():
    crear_archivos()  # Para crear los archivos antes de mostrar el menú

    while True:
        print("\n===== SISTEMA DE ASISTENCIA HERPO =====")
        print("1. Registrar trabajador")
        print("2. Marcar ingreso por código")
        print("3. Marcar salida por código")
        print("4. Buscar por código (ingresos y salidas)")
        print("5. Calcular reporte de horas y sanciones")
        print("6. Generar nómina y exportar a Excel")
        print("7. Ver trabajadores registrados")
        print("8. Salir del sistema")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_trabajador()
        elif opcion == "2":
            marcar_actividad("ingreso")
        elif opcion == "3":
            marcar_actividad("salida")
        elif opcion == "4":
            consultar_por_codigo()
        elif opcion == "5":
            calcular_reporte_horas()
        elif opcion == "6":
            generar_nomina()
        elif opcion == "7":
            listar_trabajadores()
        elif opcion == "8":
            print("Saliendo del sistema de asistencia. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Seleccione una opción del 1 al 8.")

if __name__ == "__main__":
    main()

#Ese es todo el código del sistema de asistencia y control de horas laborales para trabajadores de HERPO. :)
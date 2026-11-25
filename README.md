# Sistema de asistencia y cálculo de nómina (Basado en almacenes de ropa Herpo)
Este es un sistema de asistencia (a la jornada laboral) práctico y sencillo de usar. Permite el registro trabajadores con un código único y realizar el cálculo de nómina y exportarlo a Excel de manera rápida y efectiva.

#  Interfaz Visual
<img width="483" height="762" alt="imagen" src="https://github.com/user-attachments/assets/4855b18b-7d14-47d8-8d17-eb6449e7f54b" />

#  Problema
En la cadena de tiendas de ropa Herpo, el proceso de gestión de asistencia del personal presenta ineficiencias operativas y vulnerabilidades en la integridad de la información, debido al uso de registros manuales en planillas de papel. Esta modalidad genera errores en la captura de datos, dificulta el acceso al historial de asistencia y ralentiza el procesamiento de horas trabajadas, afectando el cálculo preciso de nómina y la aplicación justa de políticas laborales.

#  Objetivos
**Objetivo general**

Desarrollar una herramienta digital en Python que automatice el registro, consulta y procesamiento de la asistencia del personal en la cadena de tiendas de ropa Herpo, reemplazando las planillas físicas para garantizar la integridad de los datos y agilizar el cálculo de jornadas laborales y políticas internas.

**Objetivos específicos:**
- Estandarizar registros: Capturar ingresos y salidas mediante un código único de 4 dígitos (primeros 4 dígitos de la cédula).
- Almacenamiento persistente: Guardar historiales en archivos `.txt` locales para agilizar consultas y evitar pérdidas de datos.
- Automatizar cálculos: Procesar horas trabajadas, compensar excedentes diarios (más de 6 horas) al día siguiente y alertar faltas/sanciones.
- Facilitar la operación: Proveer una interfaz intuitiva en consola y entorno gráfico (Tkinter) para supervisores de tienda.
  
#  Usuarios

- Administrador_a de la sede / Personal de recursos humanos
- Empleados de la tienda (Marcar ingresos / salidas)
  
#  Requerimientos
**Funcionales**

-  Registro: Alta de empleados con nombre, apellido y código numérico único de 4 dígitos.
-  Marcación:*Registro independiente de fecha y hora exacta de entrada y salida.
-  Consulta: Búsqueda rápida del historial de actividad por código de empleado.
-  Compensación: Cálculo automático de horas; el exceso sobre 6 horas diarias se descuenta de la jornada siguiente.
-  Sanciones: Detección de marcaciones incompletas o inasistencias con generación de alertas.
  
**No Funcionales**

-  Persistencia: Creación automática y lectura de archivos planos (`Trabajadores_H.txt`, `Ingresos_H.txt`, `Salidas_H.txt`) en UTF-8.
-  Validación: Control de campos vacíos, formato numérico y longitud exacta de 4 dígitos.
-  Funcionalidad: Desarrollado en Python usando únicamente librerías estándar (`os`, `datetime`, `tkinter`).

#  Validaciones del sistema

-  Formato y longitud de código: Verifica mediante `.isdigit()` y `len() == 4` que el identificador contenga exactamente 4 caracteres numéricos.
-  Existencia y duplicidad: Evita registrar dos trabajadores con el mismo código y bloquea marcaciones o consultas de códigos inexistentes.
-  Consistencia de jornadas: Detecta turnos incompletos (entradas sin salida registrada) antes de calcular el total de horas.

#  Validaciones con usuarios
coordinadores
**Metodología:** Prueba de campo con 5 usuarios potenciales (uno que desempañaba el rol de administrador) mediante tareas autónomas (registro, marcación, consulta y generación de reporte) sin asistencia paso a paso.
* **Hallazgos clave:** Interfaz intuitiva, rápida y funcional para reemplazar el registro en papel. Se identificó una duda inicial sobre el origen del código de 4 dígitos.
* **Mejoras implementadas/priorizadas:** 
  1. Etiqueta explícita indicando que el código corresponde a los primeros 4 dígitos de la cédula.
  2. Botón de limpieza rápida de campos para agilizar consultas consecutivas.
  3. Resaltado visual en alertas de faltas y sanciones.

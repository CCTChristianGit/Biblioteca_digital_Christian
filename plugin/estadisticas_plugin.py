from datetime import date


def formatear_fecha(fecha):
    # Hace que las fechas esten en formato dd-mm-aaaa

    if fecha is None:
        return "-"

    return fecha.strftime("%d-%m-%Y")


def ejecutar(biblioteca):
    # Con la informacion de la biblioteca lista un resumen por pantalla de los datos del proyecto
    resumen = biblioteca.resumen()

    return (
        "=== ESTADISTICAS DE LA BIBLIOTECA ===\n"
        f"Fecha actual: {formatear_fecha(resumen['fecha'])}\n"
        f"Libros registrados: {resumen['libros']}\n"
        f"Usuarios registrados: {resumen['usuarios']}\n"
        f"Prestamos activos: {resumen['prestamos_activos']}\n"
    )
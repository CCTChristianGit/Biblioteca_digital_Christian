from fpdf import FPDF
from datetime import date
import os


def formatear_fecha(fecha):
    # Hace que las fechas esten en formato dd-mm-aaaa

    if fecha is None:
        return "-"

    return fecha.strftime("%d-%m-%Y")


class ExportarPDFMixin:
    """
    Mixin para exportar informacion a PDF real
    """

    def exportar_pdf(self, ruta: str, lineas: list[str]) -> None:
        # Genera un archivo PDF fisico real

        os.makedirs("exportacion", exist_ok=True) # Asegura de que sirve el directorio exportacion

        pdf = FPDF() # Inicializa el objeto fpdf
        pdf.add_page() # Crea una nueva pagina 

        pdf.set_font("Arial", size=12) # Establece la fuente

        # Itera sobre la lista de strings para escribir el contenido
        for linea in lineas:
            # cell(ancho, alto, texto, salto de linea)
            # ancho=0 expande la celda hasta el margen derecho automaticamente
            pdf.cell(0, 10, txt=linea, ln=True)

        pdf.output(ruta) # Guarda el archivo en la ruta


def ejecutar(biblioteca):

    mixin = ExportarPDFMixin()

    resumen = biblioteca.resumen()

    # Contenido del PDF que es le mismo que el resumen
    lineas = [
        "RESUMEN BIBLIOTECA",
        "",
        f"Fecha actual: {formatear_fecha(resumen['fecha'])}",
        f"Libros: {resumen['libros']}",
        f"Usuarios: {resumen['usuarios']}",
        f"Prestamos activos: {resumen['prestamos_activos']}",
    ]

    ruta = "exportacion/resumen.pdf"

    mixin.exportar_pdf(ruta, lineas)

    return f"PDF exportado en {ruta}"
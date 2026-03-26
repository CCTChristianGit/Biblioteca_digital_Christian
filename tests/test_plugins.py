import importlib
import sys
import types

from servicio.plugins import GestorPlugins


def test_listar_plugins_gestor_plugins(biblioteca):
    gestor = GestorPlugins()
    plugins = gestor.listar_plugins()

    assert plugins == sorted(plugins)
    assert "estadisticas_plugin" in plugins
    assert "exportar_pdf_plugin" in plugins


def test_ejecutar_estadisticas_plugin(biblioteca):
    gestor = GestorPlugins()

    biblioteca.agregar_libro("Libro 1", "Autor 1")
    biblioteca.registrar_usuario("Usuario 1")
    biblioteca.prestar_libro(1, 1, plazo_dias=7)

    resultado = gestor.ejecutar_plugin("estadisticas_plugin", biblioteca)
    assert "=== ESTADISTICAS DE LA BIBLIOTECA" in resultado or "ESTADISTICAS" in resultado
    assert "Libros registrados: 1" in resultado
    assert "Usuarios registrados: 1" in resultado
    assert "Prestamos activos: 1" in resultado


def test_ejecutar_exportar_pdf_plugin_con_fpdf_mock(biblioteca, monkeypatch):
    # Creamos un mock de `fpdf` para que el plugin se pueda importar sin dependencias externas.
    class FakeFPDF:
        last_instance = None

        def __init__(self):
            FakeFPDF.last_instance = self
            self.calls = []
            self.output_path = None

        def add_page(self):
            self.calls.append(("add_page",))

        def set_font(self, family, size=12):
            self.calls.append(("set_font", family, size))

        def cell(self, w, h, txt="", ln=True, **kwargs):
            self.calls.append(("cell", txt, ln))

        def output(self, ruta):
            self.output_path = ruta
            self.calls.append(("output", ruta))

    fake_fpdf = types.ModuleType("fpdf")
    fake_fpdf.FPDF = FakeFPDF

    monkeypatch.setitem(sys.modules, "fpdf", fake_fpdf)
    sys.modules.pop("plugin.exportar_pdf_plugin", None)

    mod = importlib.import_module("plugin.exportar_pdf_plugin")
    monkeypatch.setattr(mod.os, "makedirs", lambda *args, **kwargs: None)

    gestor = GestorPlugins()
    resultado = gestor.ejecutar_plugin("exportar_pdf_plugin", biblioteca)

    assert "PDF exportado en exportacion/resumen.pdf" == resultado
    assert FakeFPDF.last_instance.output_path == "exportacion/resumen.pdf"


from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

root_str = str(PROJECT_ROOT)
if root_str not in sys.path:
    # Permite importar `dominio`, `servicio` y `plugin` durante la fase de coleccion de pytest.
    sys.path.insert(0, root_str)

@pytest.fixture(autouse=True)
def _reset_domain_counters():
    """
    `Libro` y `Usuario` autoincrementan ids globalmente.
    Para que los tests sean deterministas, reiniciamos contadores.
    """
    from dominio.libro import Libro
    from dominio.usuario import Usuario

    Libro._contador_id = 1
    Usuario._contador_id = 1


@pytest.fixture()
def fecha_base() -> date:
    # Debe ser un `datetime.date` (los validadores de fechas sólo chequean tipo).
    return date(2026, 3, 26)


@pytest.fixture()
def biblioteca(fecha_base: date):
    from dominio.biblioteca import Biblioteca

    return Biblioteca(fecha_actual=fecha_base)


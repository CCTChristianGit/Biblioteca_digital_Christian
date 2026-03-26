import pytest

from servicio.multas import MultaFija, MultaPorDia, MultaStrategy
from dominio.prestamo import Prestamo
from datetime import date, timedelta


def test_multa_strategy_es_abstracta():
    with pytest.raises(TypeError):
        MultaStrategy()  # type: ignore[abstract]


def test_multa_por_dia_y_multa_fija_calculan_con_prestamo_finalizado():
    p = Prestamo(id_usuario=1, id_libro=1, fecha_inicio=date(2026, 1, 1), plazo_dias=7)
    p.registrar_devolucion(date(2026, 1, 15))  # 15 - 8 = 7 dias de retraso

    assert MultaPorDia(1.5).calcular(p) == 7 * 1.5
    assert MultaFija(20.0).calcular(p) == 20.0


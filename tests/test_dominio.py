from datetime import date, timedelta

import pytest

from dominio.libro import Libro
from dominio.prestamo import Prestamo
from dominio.usuario import Usuario


def test_libro_auto_increment_str_repr():
    Libro._contador_id = 1
    l1 = Libro("Titulo 1", "Autor A")
    l2 = Libro("Titulo 2", "Autor B")

    assert l1.id_libro == 1
    assert l2.id_libro == 2

    assert str(l1) == "[1] Titulo 1 - Autor A"
    assert "Libro" in repr(l1)
    assert "titulo='Titulo 1'" in repr(l1)


def test_usuario_auto_increment_str_repr():
    Usuario._contador_id = 1
    u1 = Usuario("Ana")
    u2 = Usuario("Luis")

    assert u1.id_usuario == 1
    assert u2.id_usuario == 2

    assert str(u1) == "[1] Ana"
    assert "Usuario" in repr(u1)


def test_prestamo_fecha_limite():
    fecha_inicio = date(2026, 1, 1)
    p = Prestamo(id_usuario=1, id_libro=1, fecha_inicio=fecha_inicio, plazo_dias=10)

    assert p.fecha_limite() == date(2026, 1, 11)


def test_prestamo_esta_vencido_activo_en_borde_y_despues():
    fecha_inicio = date(2026, 1, 1)
    p = Prestamo(id_usuario=1, id_libro=1, fecha_inicio=fecha_inicio, plazo_dias=10)
    limite = p.fecha_limite()

    assert p.fecha_devolucion is None
    assert p.esta_vencido(limite) is False  # se vence solo si es ">" y no ">="
    assert p.esta_vencido(limite + timedelta(days=1)) is True


def test_prestamo_esta_vencido_finalizado_segunda_regla():
    fecha_inicio = date(2026, 1, 1)
    p = Prestamo(id_usuario=1, id_libro=1, fecha_inicio=fecha_inicio, plazo_dias=10)
    limite = p.fecha_limite()

    p.registrar_devolucion(limite + timedelta(days=2))
    assert p.esta_vencido(date(2026, 2, 1)) is True

    p2 = Prestamo(id_usuario=1, id_libro=1, fecha_inicio=fecha_inicio, plazo_dias=10)
    p2.registrar_devolucion(limite - timedelta(days=1))
    assert p2.esta_vencido(date(2026, 2, 1)) is False


def test_registrar_devolucion_no_puede_ser_antes_de_inicio():
    fecha_inicio = date(2026, 1, 10)
    p = Prestamo(id_usuario=1, id_libro=1, fecha_inicio=fecha_inicio, plazo_dias=5)

    with pytest.raises(ValueError):
        p.registrar_devolucion(fecha_inicio - timedelta(days=1))


def test_dias_retraso_para_prestamo_devuelto_y_no_devuelto():
    fecha_inicio = date(2026, 1, 1)
    p = Prestamo(id_usuario=1, id_libro=1, fecha_inicio=fecha_inicio, plazo_dias=10)
    limite = p.fecha_limite()

    assert p.dias_retraso(fecha_referencia=limite) == 0
    assert p.dias_retraso(fecha_referencia=limite + timedelta(days=3)) == 3

    p.registrar_devolucion(limite + timedelta(days=2))
    assert p.dias_retraso() == 2


def test_dias_retraso_no_devuelto_sin_referencia_lanza_error():
    fecha_inicio = date(2026, 1, 1)
    p = Prestamo(id_usuario=1, id_libro=1, fecha_inicio=fecha_inicio, plazo_dias=10)

    with pytest.raises(ValueError):
        p.dias_retraso()


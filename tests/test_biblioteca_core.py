from datetime import timedelta, date

import pytest

from dominio.biblioteca import Biblioteca
from servicio.multas import MultaFija, MultaPorDia


def test_biblioteca_agregar_listar_buscar_iter_getitem_len_str(biblioteca):
    l1 = biblioteca.agregar_libro("Cien Años de Soledad", "G. García Márquez")
    l2 = biblioteca.agregar_libro("El extranjero", "Albert Camus")

    u1 = biblioteca.registrar_usuario("Ana")
    u2 = biblioteca.registrar_usuario("Luis")

    assert len(biblioteca) == 2
    bib_list = list(iter(biblioteca))
    assert bib_list[0].id_libro == 1

    assert biblioteca[l1.id_libro] is l1
    assert str(biblioteca).startswith("Biblioteca(")

    assert biblioteca.buscar_libro_por_id(l2.id_libro) is l2
    assert biblioteca.buscar_libro_por_id(999) is None

    assert biblioteca.buscar_libros_por_titulo("cien") == [l1]
    assert biblioteca.buscar_libros_por_autor("camus") == [l2]

    assert biblioteca.buscar_usuario_por_id(u2.id_usuario) is u2
    assert biblioteca.buscar_usuario_por_nombre("an") == [u1]


def test_biblioteca_eliminar_libro_y_usuario_validaciones(biblioteca):
    biblioteca.agregar_libro("Libro", "Autor")
    biblioteca.registrar_usuario("Usuario")

    with pytest.raises(ValueError):
        biblioteca.eliminar_libro(999)

    with pytest.raises(ValueError):
        biblioteca.eliminar_usuario(999)


def test_prestar_devolver_libro_y_multas(biblioteca):
    libro = biblioteca.agregar_libro("Libro de Prueba", "Autor")
    usuario = biblioteca.registrar_usuario("Usuario A")

    prestamo = biblioteca.prestar_libro(usuario.id_usuario, libro.id_libro, plazo_dias=7)
    assert prestamo.fecha_inicio == biblioteca.fecha_actual
    assert prestamo.fecha_limite() == biblioteca.fecha_actual + timedelta(days=7)
    assert biblioteca.libro_esta_prestado(libro.id_libro) is True
    assert prestamo in biblioteca.listar_prestamos_activos()

    fecha_devolucion_tarde = biblioteca.fecha_actual + timedelta(days=10)
    prestamo_finalizado = biblioteca.devolver_libro(libro.id_libro, fecha_devolucion_tarde)

    assert prestamo_finalizado.fecha_devolucion == fecha_devolucion_tarde
    assert biblioteca.libro_esta_prestado(libro.id_libro) is False
    assert prestamo_finalizado in biblioteca.prestamos_finalizados()

    # Multa por dia: retraso = 10 - 7 = 3 dias
    biblioteca.cambiar_estrategia_multa(MultaPorDia(2.5))
    multa_por_dia = biblioteca.calcular_multa(prestamo_finalizado)
    assert multa_por_dia == 3 * 2.5

    # Multa fija: si hay retraso -> importe, si no -> 0
    biblioteca.cambiar_estrategia_multa(MultaFija(10.0))
    multa_fija = biblioteca.calcular_multa(prestamo_finalizado)
    assert multa_fija == 10.0

    # Cambiar a una devolucion a tiempo
    libro2 = biblioteca.agregar_libro("Libro2", "Autor2")
    prestamo2 = biblioteca.prestar_libro(usuario.id_usuario, libro2.id_libro, plazo_dias=7)
    prestamo2_final = biblioteca.devolver_libro(libro2.id_libro, biblioteca.fecha_actual + timedelta(days=7))
    biblioteca.cambiar_estrategia_multa(MultaFija(99.0))
    assert biblioteca.calcular_multa(prestamo2_final) == 0


def test_cambiar_estrategia_multa_typecheck(biblioteca):
    with pytest.raises(TypeError):
        biblioteca.cambiar_estrategia_multa("no-es-estrategia")  # type: ignore[arg-type]


def test_eliminar_libro_no_permite_si_esta_prestado(biblioteca):
    libro = biblioteca.agregar_libro("Libro", "Autor")
    usuario = biblioteca.registrar_usuario("Usuario")
    biblioteca.prestar_libro(usuario.id_usuario, libro.id_libro, plazo_dias=5)

    with pytest.raises(ValueError):
        biblioteca.eliminar_libro(libro.id_libro)


def test_eliminar_usuario_no_permite_si_tiene_prestamos_activos(biblioteca):
    libro = biblioteca.agregar_libro("Libro", "Autor")
    usuario = biblioteca.registrar_usuario("Usuario")
    biblioteca.prestar_libro(usuario.id_usuario, libro.id_libro, plazo_dias=5)

    with pytest.raises(ValueError):
        biblioteca.eliminar_usuario(usuario.id_usuario)


def test_prestar_libro_con_libro_ya_prestado_lanza_error(biblioteca):
    libro = biblioteca.agregar_libro("Libro", "Autor")
    usuario = biblioteca.registrar_usuario("Usuario")

    biblioteca.prestar_libro(usuario.id_usuario, libro.id_libro, plazo_dias=5)
    with pytest.raises(ValueError):
        biblioteca.prestar_libro(usuario.id_usuario, libro.id_libro, plazo_dias=7)


def test_devolver_libro_que_no_esta_prestado_lanza_error(biblioteca):
    libro = biblioteca.agregar_libro("Libro", "Autor")
    biblioteca.registrar_usuario("Usuario")

    with pytest.raises(ValueError):
        biblioteca.devolver_libro(libro.id_libro, biblioteca.fecha_actual)


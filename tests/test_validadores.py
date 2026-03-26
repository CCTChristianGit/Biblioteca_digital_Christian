import pytest


def test_validar_textos_no_vacios_rechaza_vacio_y_tipo(biblioteca):
    with pytest.raises(ValueError):
        biblioteca.agregar_libro("", "Autor")

    with pytest.raises(TypeError):
        biblioteca.agregar_libro(123, "Autor")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        biblioteca.registrar_usuario("   ")


def test_validar_enteros_positivos_rechaza_no_positivo(biblioteca):
    # No existe validacion de existencia todavía porque el decorador falla primero.
    with pytest.raises(ValueError):
        biblioteca.prestar_libro(1, 1, 0)

    with pytest.raises(TypeError):
        biblioteca.prestar_libro("1", 1, 10)  # type: ignore[arg-type]


def test_validar_fechas_rechaza_no_date(biblioteca):
    with pytest.raises(TypeError):
        biblioteca.cambiar_fecha_actual("2020-01-01")  # type: ignore[arg-type]


def test_validar_devolver_libro_por_tipos(biblioteca):
    # Validadores deben disparar antes de evaluar existencia del prestamo.
    with pytest.raises(ValueError):
        biblioteca.devolver_libro(0, biblioteca.fecha_actual)  # type: ignore[arg-type]


import pytest

from dominio.metaclase import MetaclaseEntidad


def test_metaclase_exige_docstring():
    # Falta docstring, pero incluye __init__/__str__/__repr__
    with pytest.raises(TypeError) as exc:
        class EntidadSinDoc(metaclass=MetaclaseEntidad):  # noqa: D106
            def __init__(self, x):
                self.x = x

            def __str__(self):
                return str(self.x)

            def __repr__(self):
                return f"EntidadSinDoc(x={self.x})"

    assert "docstring" in str(exc.value)


def test_metaclase_exige_init_str_y_repr():
    with pytest.raises(TypeError) as exc:
        class EntidadSinInit(metaclass=MetaclaseEntidad):
            """Docstring OK"""

            def __str__(self):
                return "x"

            def __repr__(self):
                return "x"

    # Puede fallar por varios criterios, pero al menos debe indicar init
    assert "__init__" in str(exc.value)


def test_metaclase_permite_clase_valida():
    class EntidadValida(metaclass=MetaclaseEntidad):
        """Docstring OK"""

        def __init__(self, x):
            self.x = x

        def __str__(self):
            return f"Valor={self.x}"

        def __repr__(self):
            return f"EntidadValida(x={self.x!r})"

    obj = EntidadValida(10)
    assert str(obj) == "Valor=10"
    assert "EntidadValida" in repr(obj)


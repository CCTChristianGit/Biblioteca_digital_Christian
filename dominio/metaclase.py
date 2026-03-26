class MetaclaseEntidad(type):
    """
    Metaclase ligera para validar la estructura minima
    de las clases del dominio.
    """

    def __new__(mcls, name, bases, attrs):
        cls = super().__new__(mcls, name, bases, attrs)

        # Permite crear una clase base abstracta sin validarla
        if attrs.get("_omitir_validacion_metaclase", False):
            return cls

        errores = []

        # 1) Docstring obligatoria
        doc = attrs.get("__doc__")
        if doc is None or not doc.strip():
            errores.append("debe tener docstring")

        # 2) Constructor propio
        if "__init__" not in attrs:
            errores.append("debe definir __init__")

        # 3) Metodo __str__ obligatorio
        if "__str__" not in attrs:
            errores.append("debe definir __str__")

        # 4) Metodo __repr__ obligatorio
        if "__repr__" not in attrs:
            errores.append("debe definir __repr__")

        if errores:
            mensaje = f"La clase '{name}' no cumple la estructura minima: " + ", ".join(errores)
            raise TypeError(mensaje)

        return cls
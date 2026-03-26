from datetime import date
from functools import wraps
from inspect import signature


def _obtener_argumentos(func, *args, **kwargs):
    # Devuelve un diccionario con los argumentos reales recibidos

    firma = signature(func)
    argumentos = firma.bind(*args, **kwargs)
    argumentos.apply_defaults()
    return argumentos.arguments


def validar_textos_no_vacios(*nombres_parametros):
    # Valida que los parametros indicados:
    # - existan
    # - sean str
    # - no esten vacios ni solo con espacios

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            argumentos = _obtener_argumentos(func, *args, **kwargs)

            for nombre in nombres_parametros:
                valor = argumentos.get(nombre)

                if not isinstance(valor, str):
                    raise TypeError(f"El parametro '{nombre}' debe ser un texto.")

                if not valor.strip():
                    raise ValueError(f"El parametro '{nombre}' no puede estar vacio.")

            return func(*args, **kwargs)
        return wrapper
    return decorador


def validar_enteros_positivos(*nombres_parametros):
    # Valida que los parametros indicados sean enteros mayores que 0

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            argumentos = _obtener_argumentos(func, *args, **kwargs)

            for nombre in nombres_parametros:
                valor = argumentos.get(nombre)

                if not isinstance(valor, int):
                    raise TypeError(f"El parametro '{nombre}' debe ser un entero.")

                if valor <= 0:
                    raise ValueError(f"El parametro '{nombre}' debe ser mayor que 0.")

            return func(*args, **kwargs)
        return wrapper
    return decorador


def validar_fechas(*nombres_parametros):
    # Valida que los parametros indicados sean objetos datetime.date

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            argumentos = _obtener_argumentos(func, *args, **kwargs)

            for nombre in nombres_parametros:
                valor = argumentos.get(nombre)

                if not isinstance(valor, date):
                    raise TypeError(f"El parametro '{nombre}' debe ser una fecha valida.")

            return func(*args, **kwargs)
        return wrapper
    return decorador
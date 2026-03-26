from datetime import date, timedelta
from servicio.validadores import validar_fechas, validar_enteros_positivos
from dominio.metaclase import MetaclaseEntidad


class Prestamo(metaclass=MetaclaseEntidad):
    """
    Representa el prestamo de un libro a un usuario durante un plazo determinado
    """

    @validar_enteros_positivos("id_usuario", "id_libro", "plazo_dias")
    @validar_fechas("fecha_inicio")
    def __init__(self, id_usuario: int, id_libro: int, fecha_inicio: date, plazo_dias: int):
        self.id_usuario = id_usuario
        self.id_libro = id_libro
        self.fecha_inicio = fecha_inicio
        self.plazo_dias = plazo_dias
        self.fecha_devolucion = None # Se mantiene en None hasta que el libro es devuelto

    def fecha_limite(self):
        # Calcula fecha maxima de devolucion sin penalizacion
        return self.fecha_inicio + timedelta(days=self.plazo_dias)

    @validar_fechas("fecha_actual")
    def esta_vencido(self, fecha_actual: date):
        # Determina si el prestamo esta fuera de plazo
        if self.fecha_devolucion is not None:
            return self.fecha_devolucion > self.fecha_limite()
        return fecha_actual > self.fecha_limite()

    @validar_fechas("fecha_devolucion")
    def registrar_devolucion(self, fecha_devolucion: date):
        # Registra la devolucion y valida la fecha de devolucion
        if fecha_devolucion < self.fecha_inicio:
            raise ValueError("La fecha de devolucion no puede ser anterior a la fecha de inicio del prestamo")
        self.fecha_devolucion = fecha_devolucion

    def dias_retraso(self, fecha_referencia: date = None):
        # Calcula las cantidad de dias de retraso 
        fecha_comparacion = self.fecha_devolucion if self.fecha_devolucion is not None else fecha_referencia

        if fecha_comparacion is None:
            raise ValueError("Se necesita una fecha de referencia para calcular el retraso de un prestamo no devuelto")

        retraso = (fecha_comparacion - self.fecha_limite()).days
        return max(0, retraso)

    def __str__(self):
        estado = "Devuelto" if self.fecha_devolucion else "Activo"
        return (
            f"Prestamo(libro={self.id_libro}, usuario={self.id_usuario}, "
            f"inicio={self.fecha_inicio}, limite={self.fecha_limite()}, estado={estado})"
        )

    def __repr__(self):
        return (
            f"Prestamo(id_usuario={self.id_usuario}, id_libro={self.id_libro}, "
            f"fecha_inicio={self.fecha_inicio!r}, plazo_dias={self.plazo_dias}, "
            f"fecha_devolucion={self.fecha_devolucion!r})"
        )
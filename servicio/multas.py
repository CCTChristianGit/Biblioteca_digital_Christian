from abc import ABC, abstractmethod


class MultaStrategy(ABC):
    """
    Clase abstracta para calcular multas.
    Define la interfaz que deben implementar
    todas las estrategias de multa.
    """

    @abstractmethod
    def calcular(self, prestamo):
        # Debe devolver el importe de la multa

        pass


class MultaPorDia(MultaStrategy):
    """
    Multa basada en dias de retraso.
    """

    def __init__(self, importe_por_dia: float):
        self.importe_por_dia = importe_por_dia

    def calcular(self, prestamo):
        dias = prestamo.dias_retraso()
        return dias * self.importe_por_dia


class MultaFija(MultaStrategy):
    """
    Multa fija si hay retraso.
    """

    def __init__(self, importe: float):
        self.importe = importe

    def calcular(self, prestamo):
        dias = prestamo.dias_retraso()

        if dias > 0:
            return self.importe

        return 0
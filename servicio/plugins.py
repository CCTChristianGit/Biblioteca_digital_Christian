import importlib
import os


class GestorPlugins:
    """
    Carga y ejecuta plugins dinamicamente desde la carpeta plugin.
    """

    def __init__(self, carpeta_plugins="plugin"):
        self.carpeta_plugins = carpeta_plugins

    def listar_plugins(self):
        # Devuelve una lista con los nombres de los plugins disponibles
        
        if not os.path.isdir(self.carpeta_plugins):
            return []

        plugins = []

        for archivo in os.listdir(self.carpeta_plugins):
            if archivo.endswith(".py") and not archivo.startswith("_"):
                plugins.append(archivo[:-3])

        return sorted(plugins)

    def cargar_plugin(self, nombre_plugin):
        # Carga un plugin por nombre usando importlib
        
        ruta_modulo = f"{self.carpeta_plugins}.{nombre_plugin}"
        return importlib.import_module(ruta_modulo)

    def ejecutar_plugin(self, nombre_plugin, biblioteca):
        # Ejecuta la funcion 'ejecutar' del plugin indicado
        
        modulo = self.cargar_plugin(nombre_plugin)

        if not hasattr(modulo, "ejecutar"):
            raise AttributeError(
                f"El plugin '{nombre_plugin}' no tiene una funcion 'ejecutar(biblioteca)'."
            )

        return modulo.ejecutar(biblioteca)
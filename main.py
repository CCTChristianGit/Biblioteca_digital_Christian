from datetime import datetime, date
import os
from dominio.biblioteca import Biblioteca
from servicio.multas import MultaPorDia, MultaFija
from servicio.plugins import GestorPlugins

# HELPERS
def limpiar_pantalla():
    os.system("cls")

def pausar():
    input("\n PULSA ENTER PARA CONTINUAR ...")

def pedir_entero(mensaje: str) -> int:
    # Solicita un numero entero por consola
    numero_valido = False

    while not numero_valido:
        try:
            texto = input(mensaje).strip()

            if texto.lower() == "cancelar":
                return None

            valor = int(texto)
            numero_valido = True
            return valor

        except ValueError:
            print("Error: El numero debe de ser entero o escribe 'cancelar'.")

def pedir_decimal_positivo(mensaje: str) -> float:
    # Solicita un numero decimal (float) y valida que sea mayor que cero
    while True:
        texto = input(mensaje).strip()

        if texto.lower() == "cancelar":
            return None

        try:
            valor = float(texto)
            if valor <= 0:
                print("Error: El valor debe ser mayor que 0 o escribe 'cancelar'.")
                continue
            return valor
        except ValueError:
            print("Error: Debes introducir un numero valido o escribe 'cancelar'.")

def pedir_texto_no_vacio(mensaje: str) -> str:
    #  Solicita una cadena de texto y se asegura de que no este compuesta solo por espacios
    texto_valido = False

    while not texto_valido:
        texto = input(mensaje).strip()

        if texto.lower() == "cancelar":
            return None

        if texto:
            texto_valido = True
            return texto

        print("Error: Este campo no puede estar vacio o escribe 'cancelar'.")

def formatear_fecha(fecha):
    # Convierte un objeto date a string con formato dd-mm-aaaa 
    if fecha is None:
        return "-"

    return fecha.strftime("%d-%m-%Y")

def pedir_fecha(mensaje: str) -> date:
    # Solicita una fecha en formato dd/mm/aaaa y valida un rango de años 2020-2050
    fecha_valida = False

    while not fecha_valida:
        texto = input(mensaje).strip()

        if texto.lower() == "cancelar":
            return None

        try:
            fecha = datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            print("Error: Formato no permitido. Usa dd/mm/aaaa o escribe 'cancelar'")
            continue

        if fecha.year < 2020 or fecha.year > 2050:
            print("Error: El año debe de ser entre 2020 y 2050 (para limitar)")
            continue

        fecha_valida = True
        return fecha

def pedir_fecha_con_default(mensaje: str, fecha_por_defecto: date) -> date:
    # Version de pedir_fecha que permite presionar 'Enter' para usar una fecha predefinida
    fecha_valida = False

    while not fecha_valida:
        texto = input(mensaje).strip()

        if texto.lower() == "cancelar":
            return None

        if texto == "":
            return fecha_por_defecto

        try:
            fecha = datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            print("Error: formato inválido. Usa dd/mm/aaaa, deja en blanco para usar la fecha actual o escribe 'cancelar'.")
            continue

        if fecha.year < 2020 or fecha.year > 2050:
            print("Error: el año debe estar entre 2020 y 2050.")
            continue

        return fecha

def pedir_nombre_archivo(mensaje, nombre_defecto):
    # Pide nombre de archivo.
    # - cancelar -> None
    # - vacio -> nombre_defecto
    # - texto -> texto

    texto = input(mensaje).strip()

    if texto.lower() == "cancelar":
        return None

    if texto == "":
        return nombre_defecto

    return texto


# INTERFACES DE LOS MENUS
def mostrar_menu_principal():
    print("===== SISTEMA BIBLIOTECA DIGITAL =====")
    print("[1] Opciones Libro")
    print("[2] Opciones Usuario")
    print("[3] Prestamos")
    print("[4] Devoluciones")
    print("[5] Sistema")
    print("[0] Salir")


def mostrar_menu_libros():
    print("===== OPCIONES LIBRO =====")
    print("[1] Agregar libro")
    print("[2] Eliminar libro")
    print("[3] Listar libros")
    print("[4] Buscar libro por ID")
    print("[5] Buscar libro por titulo")
    print("[6] Buscar libro por autor")
    print("[0] Cancelar")


def mostrar_menu_usuarios():
    print("===== OPCIONES USUARIO =====")
    print("[1] Agregar usuario")
    print("[2] Eliminar usuario")
    print("[3] Listar usuarios")
    print("[4] Buscar usuario por ID")
    print("[5] Buscar usuario por nombre")
    print("[6] Ver historial de usuario")
    print("[0] Cancelar")


def mostrar_menu_prestamos():
    print("===== PRESTAMOS =====")
    print("[1] Realizar prestamo")
    print("[2] Listar prestamos activos")
    print("[3] Listar prestamos vencidos")
    print("[4] Listar prestamos finalizados")
    print("[0] Cancelar")


def mostrar_menu_devolucion():
    print("===== DEVOLUCIONES =====")
    print("[1] Realizar devolucion")
    print("[2] Historial de devoluciones")
    print("[0] Cancelar")


def mostrar_menu_sistema():
    print("===== SISTEMA =====")
    print("[1] Cambiar fecha actual")
    print("[2] Cambiar estrategia de multa")
    print("[3] Exportar / Importar datos")
    print("[4] Ejecutar plugin")
    print("[0] Cancelar")


# OBTENCION DE DATOS
def obtener_nombre_libro(biblioteca: Biblioteca, id_libro: int) -> str:
    libro = biblioteca.buscar_libro_por_id(id_libro)
    return libro.titulo if libro else f"Libro ID {id_libro}"

def obtener_nombre_usuario(biblioteca: Biblioteca, id_usuario: int) -> str:
    usuario = biblioteca.buscar_usuario_por_id(id_usuario)
    return usuario.nombre if usuario else f"Usuario ID {id_usuario}"


# MOSTRAR DATOS
def mostrar_prestamo_detallado(biblioteca: Biblioteca, prestamo):
    nombre_usuario = obtener_nombre_usuario(biblioteca, prestamo.id_usuario)
    nombre_libro = obtener_nombre_libro(biblioteca, prestamo.id_libro)

    activo = prestamo.fecha_devolucion is None
    estado = "Activo" if activo else "Finalizado"

    print(f"Usuario: {nombre_usuario}")
    print(f"Libro: {nombre_libro}")
    print("Fecha inicio:", formatear_fecha(prestamo.fecha_inicio))
    print("Fecha limite:", formatear_fecha(prestamo.fecha_limite()))
    print(f"Estado: {estado}")

    if not activo:
        entregado_a_tiempo = prestamo.fecha_devolucion <= prestamo.fecha_limite()
        print("Fecha devolucion:", formatear_fecha(prestamo.fecha_devolucion))
        print(f"Entregado a tiempo: {'SI' if entregado_a_tiempo else 'NO'}")
        try:
            multa = biblioteca.calcular_multa(prestamo)
            print(f"Multa: {multa} €")
        except ValueError:
            pass

    print("\n", "-" * 20, "\n")

def mostrar_prestamo_confirmado(biblioteca: Biblioteca, prestamo):
    nombre_usuario = obtener_nombre_usuario(biblioteca, prestamo.id_usuario)
    nombre_libro = obtener_nombre_libro(biblioteca, prestamo.id_libro)

    print(f"Usuario: {nombre_usuario}")
    print(f"Libro: [{prestamo.id_libro}] {nombre_libro}")
    print("Fecha inicio:", formatear_fecha(prestamo.fecha_inicio))
    print("Fecha limite:", formatear_fecha(prestamo.fecha_limite()))
    print("\n", "-" * 20, "\n")

def mostrar_libros_no_prestados(biblioteca: Biblioteca) -> bool:
    libros = biblioteca.listar_libros()

    libros_disponibles = [
        libro for libro in libros
        if not biblioteca.libro_esta_prestado(libro.id_libro)
    ]

    if not libros_disponibles:
        print("No hay libros disponibles para prestar.")
        return False

    for libro in libros_disponibles:
        print(libro)

    return True

def mostrar_usuarios_disponibles(biblioteca: Biblioteca) -> bool:
    usuarios = biblioteca.listar_usuarios()

    if not usuarios:
        print("No hay usuarios registrados.")
        return False

    for usuario in usuarios:
        print(usuario)

    return True

def mostrar_prestamos_activos_para_devolucion(biblioteca: Biblioteca) -> bool:
    prestamos = biblioteca.listar_prestamos_activos()

    if not prestamos:
        print("No hay prestamos activos.")
        return False

    for prestamo in prestamos:
        mostrar_prestamo_confirmado(biblioteca, prestamo)

    return True


# MENU MULTAS
def menu_multas(biblioteca: Biblioteca):
    limpiar_pantalla()
    print("===== ESTRATEGIA DE MULTA =====")
    print("(Escribe 'cancelar' para cancelar la accion)\n")
    print("[1] Multa por dia")
    print("[2] Multa fija")
    print("[0] Volver")

    opcion = input("Seleccione una opcion: ").strip()

    try:
        if opcion == "1":
            importe = pedir_decimal_positivo("Importe por dia: ")
            if importe is None:
                print("\nAccion cancelada.")
                return

            biblioteca.cambiar_estrategia_multa(MultaPorDia(importe))
            print(f"\nEstrategia actualizada correctamente: multa por dia ({importe})")
            pausar()

        elif opcion == "2":
            importe = pedir_decimal_positivo("Importe fijo: ")
            if importe is None:
                print("\nAccion cancelada.")
                return

            biblioteca.cambiar_estrategia_multa(MultaFija(importe))
            print(f"\nEstrategia actualizada correctamente: multa fija ({importe})")
            pausar()

        elif opcion == "0":
            return

        else:
            print("Opcion no valida.")
            pausar()

    except ValueError as e:
        print(f"\nError: {e}")
        pausar()

# MENU EXPORTAR
def menu_exportacion(biblioteca: Biblioteca):

    limpiar_pantalla()
    print("===== EXPORTACION / IMPORTACION =====")
    print("(Escribe 'cancelar' para cancelar, Enter = nombre por defecto)\n")

    print("[1] Exportar libros CSV")
    print("[2] Exportar usuarios CSV")
    print("[3] Exportar prestamos CSV")
    print("[4] Exportar todo JSON")
    print("[5] Importar libros CSV")
    print("[6] Importar usuarios CSV")
    print("[7] Importar prestamo CSV")
    print("[8] Importar todo JSON")
    print("[0] Volver")

    opcion = input("Seleccione una opcion: ").strip()

    try:

        # ---------- EXPORTAR ----------

        if opcion == "1":

            ruta = pedir_nombre_archivo(
                "Archivo (Enter = libros.csv): ",
                "libros.csv"
            )
            if ruta is None:
                print("Cancelado")
                pausar()
                return

            biblioteca.exportar_libros_csv(ruta)
            print("Exportado correctamente")
            pausar()


        elif opcion == "2":

            ruta = pedir_nombre_archivo(
                "Archivo (Enter = usuarios.csv): ",
                "usuarios.csv"
            )
            if ruta is None:
                print("Cancelado")
                pausar()
                return

            biblioteca.exportar_usuarios_csv(ruta)
            print("Exportado correctamente")
            pausar()


        elif opcion == "3":

            ruta = pedir_nombre_archivo(
                "Archivo (Enter = prestamos.csv): ",
                "prestamos.csv"
            )
            if ruta is None:
                print("Cancelado")
                pausar()
                return

            biblioteca.exportar_prestamos_csv(ruta)
            print("Exportado correctamente")
            pausar()


        elif opcion == "4":

            ruta = pedir_nombre_archivo(
                "Archivo (Enter = datos.json): ",
                "datos.json"
            )
            if ruta is None:
                print("Cancelado")
                pausar()
                return

            biblioteca.exportar_todo_json(ruta)
            print("Exportado correctamente")
            pausar()


        # ---------- IMPORTAR ----------

        elif opcion == "5":

            ruta = pedir_nombre_archivo(
                "Archivo (Enter = libros.csv): ",
                "libros.csv"
            )
            if ruta is None:
                print("Cancelado")
                pausar()
                return

            biblioteca.importar_libros_csv(ruta)
            print("Importado correctamente")
            pausar()


        elif opcion == "6":

            ruta = pedir_nombre_archivo(
                "Archivo (Enter = usuarios.csv): ",
                "usuarios.csv"
            )
            if ruta is None:
                print("Cancelado")
                pausar()
                return

            biblioteca.importar_usuarios_csv(ruta)
            print("Importado correctamente")
            pausar()


        elif opcion == "7":
            ruta = pedir_nombre_archivo(
                "Archivo (Enter = prestamos.csv): ", 
                "prestamos.csv"
            )
            if ruta is None:
                print("Cancelado")
                pausar()
                return
            
            biblioteca.importar_prestamos_csv(ruta)
            print("Importado correctamente")
            pausar()


        elif opcion == "8":

            ruta = pedir_nombre_archivo(
                "Archivo (Enter = datos.json): ",
                "datos.json"
            )
            if ruta is None:
                print("Cancelado")
                pausar()
                return

            biblioteca.importar_todo_json(ruta)
            print("Importado correctamente")
            pausar()


        elif opcion == "0":
            return

        else:
            print("Opcion invalida")
            pausar()

    except Exception as e:
        print("Error:", e)
        pausar()

# MENU PLUGINS
def menu_plugins(biblioteca: Biblioteca):
# Este es el unico menu distinto porque tiene una carga dinamica de plugins
    limpiar_pantalla()
    print("===== PLUGINS =====")
    print("(Escribe 'cancelar' para cancelar)\n")

    gestor = GestorPlugins()
    plugins = gestor.listar_plugins()

    if not plugins:
        print("No hay plugins disponibles.")
        pausar()
        return

    for i, nombre in enumerate(plugins, start=1):
        print(f"[{i}] {nombre}")

    opcion = input("\nSeleccione un plugin: ").strip()

    if opcion.lower() == "cancelar":
        print("\nAccion cancelada.")
        return

    try:
        indice = int(opcion) - 1

        if indice < 0 or indice >= len(plugins):
            print("Opcion no valida.")
            pausar()
            return

        nombre_plugin = plugins[indice]
        resultado = gestor.ejecutar_plugin(nombre_plugin, biblioteca)

        limpiar_pantalla()
        print(f"===== RESULTADO DEL PLUGIN: {nombre_plugin} =====\n")
        print(resultado)
        pausar()

    except ValueError:
        print("Debes introducir un numero valido.")
        pausar()
    except Exception as e:
        print(f"Error al ejecutar el plugin: {e}")
        pausar()

# MENU LIBRO
def menu_libros(biblioteca: Biblioteca):
    en_menu_libros = True

    while en_menu_libros:
        limpiar_pantalla()
        mostrar_menu_libros()
        opcion = input("Selecciona una opcion: ").strip()

        try:
            if opcion == "1":
                limpiar_pantalla()
                print("===== AGREGAR LIBRO =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                titulo = pedir_texto_no_vacio("Titulo: ")
                if titulo is None:
                    print("\nAccion cancelada.")
                    continue

                autor = pedir_texto_no_vacio("Autor: ")
                if autor is None:
                    print("\nAccion cancelada.")
                    continue

                libro = biblioteca.agregar_libro(titulo, autor)
                print(f"\nLibro agregado correctamente con ID {libro.id_libro}")
                pausar()

            elif opcion == "2":
                limpiar_pantalla()
                print("===== ELIMINAR LIBRO =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                if not mostrar_libros_no_prestados(biblioteca):
                    pausar()
                    continue

                id_libro = pedir_entero("\nID del libro a eliminar: ")
                if id_libro is None:
                    print("\nAccion cancelada.")
                    continue

                libro = biblioteca.eliminar_libro(id_libro)
                print(f"\nLibro eliminado correctamente: {libro.titulo}")
                pausar()

            elif opcion == "3":
                limpiar_pantalla()
                print("===== LISTADO DE LIBROS =====")
                libros = biblioteca.listar_libros()

                if not libros:
                    print("No hay libros registrados")
                else:
                    for libro in libros:
                        print(libro)
                pausar()

            elif opcion == "4":
                limpiar_pantalla()
                print("===== BUSCAR LIBRO POR ID =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                id_libro = pedir_entero("ID del libro: ")
                if id_libro is None:
                    print("\nAccion cancelada.")
                    continue

                libro = biblioteca.buscar_libro_por_id(id_libro)

                if libro:
                    print("\nLibro encontrado:")
                    print(libro)
                else:
                    print("\nNo existe ningun libro con ese ID.")
                pausar()

            elif opcion == "5":
                limpiar_pantalla()
                print("===== BUSCAR LIBRO POR TITULO =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                texto = pedir_texto_no_vacio("Texto del titulo a buscar: ")
                if texto is None:
                    print("\nAccion cancelada.")
                    continue

                resultados = biblioteca.buscar_libros_por_titulo(texto)

                if resultados:
                    print("\n===== RESULTADOS =====")
                    for libro in resultados:
                        print(libro)
                else:
                    print("\nNo se encontraron libros con ese titulo.")
                pausar()

            elif opcion == "6":
                limpiar_pantalla()
                print("===== BUSCAR LIBRO POR AUTOR =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                texto = pedir_texto_no_vacio("Texto del autor a buscar: ")
                if texto is None:
                    print("\nAccion cancelada.")
                    continue

                resultados = biblioteca.buscar_libros_por_autor(texto)

                if resultados:
                    print("\n===== RESULTADOS =====")
                    for libro in resultados:
                        print(libro)
                else:
                    print("\nNo se encontraron libros de ese autor.")

                pausar()

            elif opcion == "0":
                en_menu_libros = False
                limpiar_pantalla()

            else:
                print("Opcion no valida.")
                pausar()

        except ValueError as e:
            print(f"\nError: {e}")
            pausar()

# MENU USUARIO
def menu_usuarios(biblioteca: Biblioteca):
    en_menu_usuarios = True

    while en_menu_usuarios:
        limpiar_pantalla()
        mostrar_menu_usuarios()
        opcion = input("Seleccione una opcion: ").strip()

        try:
            if opcion == "1":
                limpiar_pantalla()
                print("===== AGREGAR USUARIO =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                nombre = pedir_texto_no_vacio("Nombre del usuario: ")
                if nombre is None:
                    print("\nAccion cancelada.")
                    continue

                usuario = biblioteca.registrar_usuario(nombre)
                print(f"\nUsuario registrado correctamente con ID {usuario.id_usuario}")
                pausar()

            elif opcion == "2":
                limpiar_pantalla()
                print("===== ELIMINAR USUARIO =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                if not mostrar_usuarios_disponibles(biblioteca):
                    pausar()
                    continue

                id_usuario = pedir_entero("\nID del usuario a eliminar: ")
                if id_usuario is None:
                    print("\nAccion cancelada.")
                    continue

                usuario = biblioteca.eliminar_usuario(id_usuario)
                print(f"\nUsuario eliminado correctamente: {usuario.nombre}")
                pausar()

            elif opcion == "3":
                limpiar_pantalla()
                print("===== LISTADO DE USUARIOS =====")
                usuarios = biblioteca.listar_usuarios()

                if not usuarios:
                    print("No hay usuarios registrados.")
                else:
                    for usuario in usuarios:
                        print(usuario)

                pausar()

            elif opcion == "4":
                limpiar_pantalla()
                print("===== BUSCAR USUARIO POR ID =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                # if not mostrar_usuarios_disponibles(biblioteca):
                #     pausar()
                #     continue

                id_usuario = pedir_entero("ID del usuario: ")
                if id_usuario is None:
                    print("\nAccion cancelada.")
                    continue

                usuario = biblioteca.buscar_usuario_por_id(id_usuario)

                if usuario:
                    print("\nUsuario encontrado:")
                    print(usuario)
                else:
                    print("\nNo existe ningun usuario con ese ID.")

                pausar()

            elif opcion == "5":
                limpiar_pantalla()
                print("===== BUSCAR USUARIO POR NOMBRE =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                texto = pedir_texto_no_vacio("Nombre a buscar: ")
                if texto is None:
                    print("\nAccion cancelada.")
                    continue

                resultados = biblioteca.buscar_usuario_por_nombre(texto)

                if resultados:
                    print("\n===== RESULTADOS =====")
                    for usuario in resultados:
                        print(usuario)
                else:
                    print("\nNo se encontraron usuarios con ese nombre.")

                pausar()

            elif opcion == "6":
                limpiar_pantalla()
                print("===== HISTORIAL DE USUARIO =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                if not mostrar_usuarios_disponibles(biblioteca):
                    pausar()
                    continue

                id_usuario = pedir_entero("\nID del usuario: ")
                if id_usuario is None:
                    print("\nAccion cancelada.")
                    continue

                historial = biblioteca.historial_usuario(id_usuario)

                if not historial:
                    print("Ese usuario no tiene historial de prestamos.")
                else:
                    for prestamo in historial:
                        mostrar_prestamo_detallado(biblioteca, prestamo)

                pausar()

            elif opcion == "0":
                en_menu_usuarios = False
                limpiar_pantalla()

            else:
                print("Opcion no valida.")
                pausar()

        except ValueError as e:
            print(f"\nError: {e}")
            pausar()

# MENU PRESTAMO
def menu_prestamos(biblioteca: Biblioteca):
    en_menu_prestamos = True

    while en_menu_prestamos:
        limpiar_pantalla()
        mostrar_menu_prestamos()
        opcion = input("Seleccione una opcion: ").strip()

        try:
            if opcion == "1":
                limpiar_pantalla()
                print("===== REALIZAR PRESTAMO =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                print("USUARIOS DISPONIBLES:")
                if not mostrar_usuarios_disponibles(biblioteca):
                    pausar()
                    continue

                print("\nLIBROS DISPONIBLES:")
                if not mostrar_libros_no_prestados(biblioteca):
                    pausar()
                    continue

                id_usuario = pedir_entero("\nID del usuario: ")
                if id_usuario is None:
                    print("\nAccion cancelada.")
                    continue

                id_libro = pedir_entero("ID del libro: ")
                if id_libro is None:
                    print("\nAccion cancelada.")
                    continue

                plazo_dias = pedir_entero("Plazo del prestamo (dias): ")
                if plazo_dias is None:
                    print("\nAccion cancelada.")
                    continue

                prestamo = biblioteca.prestar_libro(id_usuario, id_libro, plazo_dias)
                print("\nPrestamo registrado correctamente.")
                mostrar_prestamo_confirmado(biblioteca, prestamo)
                pausar()

            elif opcion == "2":
                limpiar_pantalla()
                print("===== PRESTAMOS ACTIVOS =====")
                prestamos = biblioteca.listar_prestamos_activos()

                if not prestamos:
                    print("No hay prestamos activos.")
                else:
                    for prestamo in prestamos:
                        mostrar_prestamo_detallado(biblioteca, prestamo)

                pausar()

            elif opcion == "3":
                limpiar_pantalla()
                print("===== PRESTAMOS VENCIDOS =====")
                prestamos = biblioteca.prestamos_vencidos()

                if not prestamos:
                    print("No hay prestamos vencidos actualmente.")
                else:
                    for prestamo in prestamos:
                        mostrar_prestamo_detallado(biblioteca, prestamo)

                pausar()

            elif opcion == "4":
                limpiar_pantalla()
                print("===== PRESTAMOS FINALIZADOS =====")
                prestamos = biblioteca.prestamos_finalizados()

                if not prestamos:
                    print("No hay prestamos finalizados.")
                else:
                    for prestamo in prestamos:
                        mostrar_prestamo_detallado(biblioteca, prestamo)

                pausar()

            elif opcion == "0":
                en_menu_prestamos = False
                limpiar_pantalla()

            else:
                print("Opcion no valida.")
                pausar()

        except ValueError as e:
            print(f"\nError: {e}")
            pausar()

# MENU DEVOLUCION
def menu_devolucion(biblioteca: Biblioteca):
    en_menu_devolucion = True

    while en_menu_devolucion:
        limpiar_pantalla()
        mostrar_menu_devolucion()
        opcion = input("Seleccione una opcion: ").strip()

        try:
            if opcion == "1":
                limpiar_pantalla()
                print("===== REALIZAR DEVOLUCION =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                if not mostrar_prestamos_activos_para_devolucion(biblioteca):
                    pausar()
                    continue

                id_libro = pedir_entero("Introduce el ID del libro mostrado entre corchetes: ")
                if id_libro is None:
                    print("\nAccion cancelada.")
                    continue

                fecha_devolucion = pedir_fecha_con_default(
                    f"Fecha de devolucion (dd/mm/aaaa) \n(si se deja en blanco se usara {formatear_fecha(biblioteca.fecha_actual)}): ",
                    biblioteca.fecha_actual
                )
                if fecha_devolucion is None:
                    print("\nAccion cancelada.")
                    continue

                prestamo = biblioteca.devolver_libro(id_libro, fecha_devolucion)
                print("\nDevolucion registrada correctamente.")
                mostrar_prestamo_detallado(biblioteca, prestamo)
                pausar()

            elif opcion == "2":
                limpiar_pantalla()
                print("===== HISTORIAL DE DEVOLUCIONES =====")
                historial = biblioteca.historial_devoluciones()

                if not historial:
                    print("No hay devoluciones registradas.")
                else:
                    for prestamo in historial:
                        mostrar_prestamo_detallado(biblioteca, prestamo)

                pausar()

            elif opcion == "0":
                en_menu_devolucion = False
                limpiar_pantalla()

            else:
                print("Opcion no valida.")
                pausar()

        except ValueError as e:
            print(f"\nError: {e}")
            pausar()

# MENU SISTEMA
def menu_sistema(biblioteca: Biblioteca):
    en_menu_sistema = True

    while en_menu_sistema:
        limpiar_pantalla()
        mostrar_menu_sistema()
        opcion = input("Seleccione una opcion: ").strip()

        try:
            if opcion == "1":
                limpiar_pantalla()
                print("===== CAMBIAR FECHA ACTUAL =====")
                print("(Escribe 'cancelar' para cancelar la accion)\n")

                nueva_fecha = pedir_fecha("Nueva fecha actual (dd/mm/aaaa): ")
                if nueva_fecha is None:
                    print("\nAccion cancelada.")
                    continue

                biblioteca.cambiar_fecha_actual(nueva_fecha)
                print(f"\nFecha actual actualizada a {biblioteca.fecha_actual}")
                pausar()

            elif opcion == "2":
                menu_multas(biblioteca)

            elif opcion == "3":
                menu_exportacion(biblioteca)

            elif opcion == "4":
                menu_plugins(biblioteca)

            elif opcion == "0":
                en_menu_sistema = False
                limpiar_pantalla()

            else:
                print("Opcion no valida.")
                pausar()

        except ValueError as e:
            print(f"\nError: {e}")
            pausar()


# MAIN
limpiar_pantalla()
print("===== INICIO DEL SISTEMA BIBLIOTECA =====")
fecha_inicial = pedir_fecha("Introduce la fecha actual del sistema (dd/mm/aaaa): ")

if fecha_inicial is None:
    print("\nInicio cancelado.")
else:
    biblioteca = Biblioteca(fecha_inicial)

    en_ejecucion = True

    while en_ejecucion:
        limpiar_pantalla()
        mostrar_menu_principal()
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            menu_libros(biblioteca)

        elif opcion == "2":
            menu_usuarios(biblioteca)

        elif opcion == "3":
            menu_prestamos(biblioteca)

        elif opcion == "4":
            menu_devolucion(biblioteca)

        elif opcion == "5":
            menu_sistema(biblioteca)

        elif opcion == "0":
            limpiar_pantalla()
            print("Saliendo del sistema...")
            en_ejecucion = False

        else:
            print("Opcion no valida.")
            pausar()
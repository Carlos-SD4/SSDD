'''Cliente de directorio para el servicio de directorio de IceDrive'''

import sys
import Ice
import IceDrive

class DirectoryClient:
    '''Clase que implementa el cliente de directorio de IceDrive'''
    def __init__(self):
        self.communicator = Ice.initialize()

    def run(self, args):
        '''Método que inicializa el cliente de directorio'''
        try:
            proxy = self.communicator.stringToProxy(args[1])
            directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy)

            if not directory_service:
                print("El proxy es incorrecto")
                sys.exit(1)

            user = input("Primero de todo indica tu usuario: ")
            print("Usuario conectado:", user)
            directory_root = directory_service.getRoot(user)
            self.menu(directory_root)

        finally:
            if self.communicator:
                self.communicator.destroy()

    def menu(self, current_directory):
        '''Método que implementa el menú de opciones del cliente de directorio'''
        while True:
            print("\n")
            print("1. Mostrar subdirectorios del directorio")
            print("2. Crear un nuevo directorio")
            print("3. Eliminar un directorio")
            print("4. Mostrar archivos del directorio actual")
            print("5. Mover a algun directorio hijo")
            print("6. Crear un nuevo archivo")
            print("7. Eliminar un archivo")
            print("8. Obtener directorio padre")
            print("9. Mover al directorio padre")
            print("10. Obtener el blobid de algun archivo")
            print("11. Salir")

            choice = input("Selecciona una opción (1-11): ")

            if choice == "1":
                print("Contenido del directorio:")
                print(current_directory.getChilds())

            elif choice == "2":
                new_dir_name = input("Ingrese el nombre del nuevo subdirectorio (sin la / de ruta): ")
                new_directory = current_directory.createChild(new_dir_name)
                print(f"Subdirectorio '{new_dir_name}' creado exitosamente.")

            elif choice == "3":
                dir_to_remove = input("Ingrese el nombre del subdirectorio a eliminar (sin la / de ruta): ")
                current_directory.removeChild(dir_to_remove)
                print(f"Subdirectorio '{dir_to_remove}' eliminado.")

            elif choice == "4":
                print("Archivos en el directorio:")
                print(current_directory.getFiles())

            elif choice == "5":
                new_dir_name = input("Ingrese el nombre del nuevo directorio (sin la / de ruta): ")
                new_directory = current_directory.getChild("/"+new_dir_name)
                if new_directory:
                    current_directory = new_directory
                    print(f"Cambiado al directorio '{new_dir_name}'.")

            elif choice == "6":
                filename = input("Ingrese el nombre del nuevo archivo: ")
                blob_id = input("Ingrese el ID del archivo: ")
                current_directory.linkFile(filename, blob_id)
                print(f"Archivo '{filename}' creado exitosamente.")

            elif choice == "7":
                filename = input("Ingrese el nombre del archivo a eliminar: ")
                current_directory.unlinkFile(filename)
                print(f"Archivo '{filename}' desenlazado.")

            elif choice == "8":
                print("El padre es:",current_directory.getParent())

            elif choice == "9":
                current_directory = current_directory.getParent()
                print("Cambiado al directorio padre.")

            elif choice == "10":
                filename = input("Ingrese el nombre del archivo: ")
                print("El blob id de",filename,"es:",current_directory.getBlobId(filename))

            elif choice == "11":
                print("Saliendo del programa.")
                sys.exit(0)

            else:
                print("Opción no válida. Por favor, elige una opción del 1 al 11.")


if __name__ == '__main__':
    app = DirectoryClient()
    app.run(sys.argv)

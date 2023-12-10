# IceDrive Directory service template

This repository contains the project template for the Directory service proposed as laboratory work for the students
of Distributed Systems in the course 2023-2024.

## Alumno
-ALumno: Carlos Sánchez Díaz

-Correo: carlos.sanchez74@alu.uclm.es

-Grupo de laboratorio: C1

## Contenido del proyecto

El objetivo principal del proyecto es desarrollar un sistema distribuido basado en varios servicios.
Para ello, se implementará un sistema de gestión de archivos de forma remota similar a One Drive de
Microsoft o Google Drive de Google.

## Servicio Directory
Este servicio permite crear una estructura de árbol en la que cada nodo puede almacenar enlaces a
ficheros de manera similar a como funciona un sistema de ficheros de disco. El servicio se
implementa mediante dos interfaces: ::IceDrive::Directory y ::IceDrive::DirectoryService.

Interfaz ::IceDrive::DirectoryService: La clase DirectoryService implementa la interfaz IceDrive.DirectoryService, siendo parte de un sistema distribuido para la gestión remota de archivos. Su función principal es crear y gestionar usuarios, así como facilitar el acceso a los directorios asociados a cada usuario.

::IceDrive::Directory:La clase Directory implementa la interfaz IceDrive.Directory para gestionar directorios y archivos en un sistema distribuido. Algunas funciones clave incluyen la creación y eliminación de directorios hijos, la gestión de archivos y la obtención de información sobre el directorio y sus contenidos.

Para lograr la persistencia de datos y retomar el programa desde donde se detuvo, es esencial tener en cuenta que la información se guarda en el archivo "user_data.json".

## Cosas a tener en cuenta
En mi programa, he implementado una funcionalidad que facilita la creación automática de usuarios cuando se introduce un nombre que no existe en el sistema. En este caso, el programa genera automáticamente un perfil para el nuevo usuario y lo añade a nuestro archivo de persistencia. Además, se crea automáticamente un directorio raíz asociado con el nombre del usuario. Por ejemplo, si registramos a una persona con el nombre "Luis", el programa generará su perfil y creará un directorio raíz llamado "/Luis". Esta implementación garantiza que no haya usuarios sin un directorio raíz asociado, asegurando una estructura coherente y completa para cada usuario registrado en el sistema.

En el proceso de creación, eliminación y navegación de directorios en nuestro programa, es crucial que el usuario ingrese el nombre del directorio sin incluir la barra ("/"). La barra ("/") se añade automáticamente según sea necesario. Es importante tener en cuenta que, aunque en la opción de mostrar los directorios se visualice con una barra ("/), al ingresar o especificar el nombre, es necesario introducir simplemente el nombre sin la barra. Si el usuario introduce un nombre con la barra ("/"), se generará una excepción para indicar que no se puede utilizar una barra en el nombre del directorio. Esta práctica asegura una interacción coherente y evita posibles inconvenientes asociados con la introducción de nombres de directorios inválidos.

En relación con los archivos y para asegurar la correcta utilización de los métodos de creación, eliminación y obtención de blobid, es necesario especificar el nombre completo del archivo, incluyendo su extensión. Al proporcionar el nombre completo con la extensión, nuestro programa puede llevar a cabo estas operaciones de manera precisa y eficiente. De esta manera, garantizamos que las acciones relacionadas con archivos se realicen de acuerdo con las expectativas del usuario, asegurando la coherencia en la manipulación de archivos y evitando posibles confusiones.

## Ejecucion del programa:
Para una correcta ejecución del proyecto, distinguimos entre el lado del servidor y el lado del cliente.

Lado del Servidor:

Ejecute el programa del servidor con el siguiente comando:

    icedrive-directory --Ice.Config=config/directory.config

Asegúrese de estar en el directorio correcto. Al ejecutarlo, obtendrá el proxy de la interfaz DirectoryService.

Lado del Cliente:

Abra otra ventana de terminal y vaya al directorio donde se encuentra el archivo del cliente, como es en mi caso, "my_directory.py".

Ejecute el siguiente comando:

    python3 my_directory.py 'proxy_del_servidor'

Coloque el proxy proporcionado por el servidor entre las comillas simples para conectarse a su interfaz.

Con estos pasos, el cliente dispondrá de un menú interactivo que le permite realizar diversas acciones típicas de un gestor de archivos con estructura de árbol.




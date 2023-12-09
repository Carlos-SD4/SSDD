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


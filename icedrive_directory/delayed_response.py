"""Servant implementation for the delayed response mechanism."""

import Ice

import IceDrive


class DirectoryQueryResponse(IceDrive.DirectoryQueryResponse):
    """Query response receiver."""
    def rootDirectoryResponse(self, root: IceDrive.DirectoryPrx, current: Ice.Current = None) -> None:
        """Receive a Directory when other service instance knows the user."""
        '''En esta clase mandamos la respuesta del directorio raiz'''


class DirectoryQuery(IceDrive.DirectoryQuery):
    """Query receiver."""
    def rootDirectory(self, user: IceDrive.UserPrx, response: IceDrive.DirectoryQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about the user's root directory."""
        '''En esta clase recibimos la peticion de un usuario para obtener su directorio raiz
        -Comprobamos que si tenemos ese directorio raiz
        -Si lo tenemos creamos la clase DirectoryQueryResponse y le pasamos el directorio raiz
        -Si no lo tenemos llamamos a los demas proxy de directorio para ver si lo tienen
        -Si ninguno lo tiene creamos el directorio raiz y se lo pasamos al usuario
        -Una vez con el proxy del directorio raiz se lo pasamos a la clase DirectoryQueryResponse
        -La respuesta se la tenemos que enviar al proxy de la variable response
        '''
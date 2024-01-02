"""Servant implementation for the delayed response mechanism."""

import Ice
import IceDrive
import json
from .directory import Directory


class DirectoryQueryResponse(IceDrive.DirectoryQueryResponse):
    """Query response receiver."""
    def rootDirectoryResponse(self, root: IceDrive.DirectoryPrx, current: Ice.Current = None) -> None:
        """Receive a Directory when other service instance knows the user."""
        DirectoryPersistence.save(root)


class DirectoryQuery(IceDrive.DirectoryQuery):

    file_path = "user_data.json"
    """Query receiver."""
    def rootDirectory(self, user: IceDrive.UserPrx, response: IceDrive.DirectoryQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about the user's root directory."""
        nombre=user.getUsername()
        if self.does_user_exist(nombre) == True:
            root_directory = self.get_root_directory_for_user(nombre)
            root_directoryprx= IceDrive.DirectoryPrx.uncheckedCast(current.adapter.addWithUUID(root_directory))
            response.rootDirectoryResponse(root_directoryprx)

    def does_user_exist(self, user: str) -> bool:
        """Check if the user exists in the user data."""
        user_data = self._load_user_data()
        usuarios = user_data.get("usuarios", [])
        return any(usuario.get("nombre") == user for usuario in usuarios)

    def get_root_directory_for_user(self, user: str) -> Directory:
        """Get the root directory for the given user."""
        user_data = self._load_user_data()

        for usuario in user_data["usuarios"]:
            if usuario["nombre"] == user:
                root_directory_info = usuario["directorios"][0]
                root_directory = Directory(root_directory_info["nombre"], user)
                return root_directory
        return None

    def _load_user_data(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}


class DirectoryPersistence():
    """Persistence class for service discovery."""
    root = None

    def save(self,root: IceDrive.DirectoryPrx):
        self.root= root

    def getroot(self):
        return self.root

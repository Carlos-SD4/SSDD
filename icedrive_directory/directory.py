"""Module for servants implementations."""

from typing import List
import json
import Ice
import IceDrive


class Directory(IceDrive.Directory):
    """Implementation of the IceDrive.Directory interface."""
        def __init__(self, name: str, user_name: str):
        self.user_name = user_name
        self.name = name
        self.parent = None
        self.childs = {}
        self.files = {}

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to the parent directory, if it exists. None in other case."""
        if self.parent is None:
            return None
        else:
            return IceDrive.DirectoryPrx.uncheckedCast(current.adapter.addWithUUID(self.parent))

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        """Return a list of names of the directories contained in the directory."""
        return list(self.childs.keys())

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to one specific directory inside the current one."""
        return IceDrive.DirectoryPrx.uncheckedCast(current.adapter.addWithUUID(self.childs.get(name)))
        
    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Create a new child directory and returns its proxy."""

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        """Remove the child directory with the given name if exists."""

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        """Return a list of the files linked inside the current directory."""
        return list(self.files.keys())

    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        """Return the "blob id" for a given file name inside the directory."""

    def linkFile(
        self, filename: str, blob_id: str, current: Ice.Current = None
    ) -> None:
        """Link a file to a given blob_id."""

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        """Unlink (remove) a filename from the current directory."""


class DirectoryService(IceDrive.DirectoryService):
    """Implementation of the IceDrive.Directory interface."""
    
    file_path = 'user_data.json'

    def __init__(self):
        self.user_directories: List[str, Directory] = {}
        
    def getRoot(self, user: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy for the root directory of the given user."""
        user_directory = self.user_directories.get(user)
        if not user_directory:
            if not self.doesUserExist(user):
                self.createUser(user)
        return IceDrive.DirectoryPrx.uncheckedCast(current.adapter.addWithUUID(user_directory))

    def doesUserExist(self, user: str) -> bool:
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
                usuarios = data.get("usuarios", [])
                existe = any(usuario.get("nombre") == user for usuario in usuarios)
                return existe

        except FileNotFoundError:
            return False

    def createUser(self, user: str) -> None:
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
        nuevo_usuario = {
            "nombre": user,
            "id": len(data.get("usuarios", [])) + 1,  # Asignar un nuevo ID
            "directorios": [
                {
                    "nombre": f"/{user}",
                    "padre": None,
                    "archivos": []
                }
            ]
        }
        data.setdefault("usuarios", []).append(nuevo_usuario)
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=2)
        

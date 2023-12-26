"""Module for servants implementations."""

# pylint: disable=import-error
# pylint: disable=no-member
# pylint: disable=unused-argument
# pylint: disable=no-self-use
# pylint: disable=no-self-argument
# pylint: disable=invalid-name
# pylint: disable=no-name-in-module

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
        self.user_data_file = "user_data.json"

    def _load_user_data(self):
        with open(self.user_data_file, "r",encoding="utf-8") as f:
            return json.load(f)

    def _update_file_info(self, filename, blob_id):
        user_data = self._load_user_data()
        user = self._get_user(user_data)
        if user:
            for directorio_info in user.get("directorios", []):
                if directorio_info["nombre"] == self.name:
                    archivos = directorio_info.get("archivos", [])
                    archivos.append({
                        "nombre": filename,
                        "blobid": blob_id
                    })
                    directorio_info["archivos"] = archivos
            self._save_user_data(user_data)

    def _save_user_data(self, user_data):
        with open(self.user_data_file, "w",encoding="utf-8") as f:
            json.dump(user_data, f, indent=2)

    def _get_user(self, user_data):
        return next((u for u in user_data["usuarios"] if u["nombre"] == self.user_name), None)

    def _update_directory_info(self, user, name, parent_name=None):
        if user:
            if "directorios" not in user:
                user["directorios"] = []
            user["directorios"].append({
                "nombre": "/"+name,
                "padre": parent_name,
                "archivos": []
            })

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to the parent directory, if it exists. None in other case."""
        if self.parent is None:
            raise IceDrive.RootHasNoParent
        return IceDrive.DirectoryPrx.uncheckedCast(current.adapter.addWithUUID(self.parent))

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        """Return a list of names of the directories contained in the directory."""
        return list(self.childs.keys())

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to one specific directory inside the current one."""
        if self.childs.get(name) is None:
            raise IceDrive.ChildNotExists
        return IceDrive.DirectoryPrx.uncheckedCast(current.adapter.addWithUUID
                                                (self.childs.get(name)))

    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Create a new child directory and returns its proxy."""
        if self.childs.get(name) is not None:
            raise IceDrive.ChildAlreadyExists
        child_directory = Directory("/"+name, user_name=self.user_name)
        child_directory.parent = self
        self.childs["/"+name] = child_directory
        user_data = self._load_user_data()
        user = self._get_user(user_data)

        if user:
            self._update_directory_info(user, name, self.name)
            self._save_user_data(user_data)

        return IceDrive.DirectoryPrx.uncheckedCast(current.adapter.addWithUUID(child_directory))


    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        """Remove the child directory with the given name if exists."""
        child_directory = self.childs.get("/"+name)
        if child_directory:
            del self.childs["/"+name]
            user_data = self._load_user_data()
            user = self._get_user(user_data)
            if user:
                user["directorios"] = [d for d in user.get("directorios", [])
                                    if d["nombre"] != "/"+name]
            self._save_user_data(user_data)
        else:
            raise IceDrive.ChildNotExists

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        """Return a list of the files linked inside the current directory."""
        return list(self.files.keys())

    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        """Return the "blob id" for a given file name inside the directory."""
        if filename not in self.files:
            raise IceDrive.FileNotFound
        user_data = self._load_user_data()
        user = self._get_user(user_data)
        for directorio_info in user.get("directorios", []):
            if directorio_info["nombre"] == self.name:
                archivos = directorio_info.get("archivos", [])
                for archivo in archivos:
                    if archivo["nombre"] == filename:
                        return archivo["blobid"]
        return ""

    def linkFile(self, filename: str, blob_id: str, current: Ice.Current = None) -> None:
        """Link a file to a given blob_id."""
        if filename in self.files:
            raise IceDrive.FileAlreadyExists(filename)
        self.files[filename] = blob_id
        self._update_file_info(filename, blob_id)

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        """Unlink (remove) a filename from the current directory."""
        if filename not in self.files:
            raise IceDrive.FileNotFound(filename)
        del self.files[filename]
        user_data = self._load_user_data()
        user = self._get_user(user_data)
        if user:
            for directorio_info in user.get("directorios", []):
                if directorio_info["nombre"] == self.name:
                    archivos = directorio_info.get("archivos", [])
                    archivos = [archivo for archivo in archivos if archivo["nombre"] != filename]
                    directorio_info["archivos"] = archivos
        self._save_user_data(user_data)



class DirectoryService(IceDrive.DirectoryService):
    """Implementation of the IceDrive.DirectoryService interface."""

    file_path = 'user_data.json'

    def __init__(self):
        self.user_directories: List[str, Directory] = {}

    def _load_user_data(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def _save_user_data(self, data):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def _get_user(user_data, user):
        usuarios = user_data.get("usuarios", [])
        return next((usuario for usuario in usuarios if usuario["nombre"] == user), None)

    def getRoot(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy for the root directory of the given user."""
        user_directory = self.user_directories.get(user)

        if not user_directory:
            if not self.does_user_exist(user):
                self.create_user(user)

            user_directory = self.get_root_directory_for_user(user)
            self.user_directories[user] = user_directory

        return IceDrive.DirectoryPrx.uncheckedCast(current.adapter.addWithUUID(user_directory))

    def does_user_exist(self, user: str) -> bool:
        """Check if the user exists in the user data."""
        user_data = self._load_user_data()
        usuarios = user_data.get("usuarios", [])
        return any(usuario.get("nombre") == user for usuario in usuarios)

    def create_user(self, user: str) -> None:
        """Create a new user with the given username."""
        user_data = self._load_user_data()

        nuevo_usuario = {
            "nombre": user,
            "id": len(user_data.get("usuarios", [])) + 1,
            "directorios": [
                {
                    "nombre": f"/{user}",
                    "padre": None,
                    "archivos": []
                }
            ]
        }
        user_data.setdefault("usuarios", []).append(nuevo_usuario)

        self._save_user_data(user_data)

    def get_root_directory_for_user(self, user: str) -> Directory:
        """Get the root directory for the given user."""
        user_data = self._load_user_data()

        for usuario in user_data["usuarios"]:
            if usuario["nombre"] == user:
                root_directory_info = usuario["directorios"][0]
                root_directory = Directory(root_directory_info["nombre"], user)
                return self.load_directory_info(root_directory, usuario, user)
        return None

    def load_directory_info(self, directory: Directory, user_info: dict,
                        user: str, is_root: bool = True) -> Directory:
        """Load directory information from user data."""
        user_directories = user_info.get("directorios", [])

        for item_info in user_directories:
            item_name = item_info["nombre"]
            item_archivos = item_info.get("archivos", [])

            if item_info["padre"] is None and is_root:
                for archivo_info in item_archivos:
                    archivo_nombre = archivo_info["nombre"]
                    archivo_blobid = archivo_info["blobid"]
                    directory.files[archivo_nombre] = archivo_blobid

            elif item_info["padre"] == directory.name:
                child_directory = Directory(item_name, user)
                child_directory.parent = directory
                directory.childs[item_name] = child_directory

                for archivo_info in item_archivos:
                    archivo_nombre = archivo_info["nombre"]
                    archivo_blobid = archivo_info["blobid"]
                    child_directory.files[archivo_nombre] = archivo_blobid

                self.load_directory_info(child_directory, user_info, user, is_root=False)
        return directory

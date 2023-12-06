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
    
    def _load_user_data(self):
        with open(self.user_data_file, "r") as f:
            return json.load(f)

    def _save_user_data(self, user_data):
        with open(self.user_data_file, "w") as f:
            json.dump(user_data, f, indent=2)

    def _get_user(self, user_data):
        return next((u for u in user_data["usuarios"] if u["nombre"] == self.user_name), None)

    def _update_directory_info(self, user, name, parent_name=None):
        if user:
            if "directorios" not in user:
                user["directorios"] = []
            user["directorios"].append({
                "nombre": name,
                "padre": parent_name,
                "archivos": []
            })
    
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
        try:
            if name in self.childs:
                raise ChildAlreadyExists(childName=name, path=self.name)

            child_directory = Directory("/" + name, user_name=self.user_name)
            child_directory.parent = self
            self.childs["/" + name] = child_directory

            parent_directory = self.getChild("/")
            if parent_directory:
                user_data = self._load_user_data()
                user = self._get_user(user_data)
                self._update_directory_info(user, "/" + name, self.name)

                self._save_user_data(user_data)
                return IceDrive.DirectoryPrx.uncheckedCast(current.adapter.addWithUUID(child_directory))
            else:
                raise ChildNotExists(childName=self.name, path="/")
        except (ChildNotExists, ChildAlreadyExists) as e:
            print(f"Error creating child directory: {e}")

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        """Remove the child directory with the given name if exists."""
        child_directory = self.childs["/" + name]
        if child_directory:
            del self.childs["/" + name]

            user_data = self._load_user_data()
            user = self._get_user(user_data)
            if user:
                user["directorios"] = [d for d in user.get("directorios", []) if d["nombre"] != "/" + name]

            self._save_user_data(user_data)

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        """Return a list of the files linked inside the current directory."""
        return list(self.files.keys())

    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        """Return the "blob id" for a given file name inside the directory."""
        try:
            user_data = self._load_user_data()
            user = self._get_user(user_data)
            if user:
                for directorio_info in user.get("directorios", []):
                    if directorio_info["nombre"] == self.name:
                        archivos = directorio_info.get("archivos", [])
                        for archivo in archivos:
                            if archivo["nombre"] == filename:
                                return archivo["blobid"]
                raise FileNotFound(filename=filename)
            else:
                raise FileNotFound(filename=filename)
        except FileNotFound as e:
            print(f"Error getting blob id for file: {e}")
            return ""

    def linkFile(
        self, filename: str, blob_id: str, current: Ice.Current = None
    ) -> None:
        """Link a file to a given blob_id."""
        if filename in self.files:
            raise IceDrive.FileAlreadyExists(filename)
        self.files[filename] = blob_id
        self._update_file_info(filename, blob_id)

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        """Unlink (remove) a filename from the current directory."""
        try:
            if filename not in self.files:
                raise FileNotFound(filename=filename)

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
        except FileNotFound as e:
            print(f"Error unlinking file: {e}")
            
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
            user_directory = self.getRootDirectoryForUser(user)
            self.user_directories[user] = user_directory

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

    def getRootDirectoryForUser(self, user: str) -> Directory:
        with open(self.file_path, "r") as file:
            data = json.load(file)

        for usuario in data["usuarios"]:
            if usuario["nombre"] == user:
                root_directory_info = usuario["directorios"][0]
                root_directory = Directory(root_directory_info["nombre"], user)
                return self.loadDirectoryInfo(root_directory, usuario, data, user)

    def loadDirectoryInfo(self, directory: Directory, user_info: dict, data: dict, user: str, is_root: bool = True) -> Directory:
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

                self.loadDirectoryInfo(child_directory, user_info, data, user, is_root=False)

        return directory
        

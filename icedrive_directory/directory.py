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
import threading
import Ice
import IceDrive
from .discovery import DiscoveryPersistence
from .delayed_response import DirectoryQueryResponse


class Directory(IceDrive.Directory):
    """Implementation of the IceDrive.Directory interface."""

    persistencia_discovery = DiscoveryPersistence()

    def __init__(self, name: str, user_name: str, user):
        self.user = user
        self.user_name = user_name
        self.name = name
        self.parent = None
        self.childs = {}
        self.files = {}
        self.user_data_file = "user_data.json"

    def _load_user_data(self):
        with open(self.user_data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _update_file_info(self, filename, blob_id):
        user_data = self._load_user_data()
        user = self._get_user(user_data)
        if user:
            for directorio_info in user.get("directorios", []):
                if directorio_info["nombre"] == self.name:
                    archivos = directorio_info.get("archivos", [])
                    archivos.append({"nombre": filename, "blobid": blob_id})
                    directorio_info["archivos"] = archivos
            self._save_user_data(user_data)

    def _save_user_data(self, user_data):
        with open(self.user_data_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2)

    def _get_user(self, user_data):
        return next(
            (u for u in user_data["usuarios"] if u["nombre"] == self.user_name), None
        )

    def _update_directory_info(self, user, name, parent_name=None):
        if user:
            if "directorios" not in user:
                user["directorios"] = []
            user["directorios"].append(
                {"nombre": "/" + name, "padre": parent_name, "archivos": []}
            )

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to the parent directory, if it exists. None in other case."""
        if self.user.isAlive() is True:
            if self.parent is None:
                raise IceDrive.RootHasNoParent
            return IceDrive.DirectoryPrx.uncheckedCast(
                current.adapter.addWithUUID(self.parent)
            )
        return None

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        """Return a list of names of the directories contained in the directory."""
        if self.user.isAlive() is True:
            return list(self.childs.keys())
        return None

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to one specific directory inside the current one."""
        if self.user.isAlive() is True:
            if self.childs.get(name) is None:
                raise IceDrive.ChildNotExists
            return IceDrive.DirectoryPrx.uncheckedCast(
                current.adapter.addWithUUID(self.childs.get(name))
            )
        return None

    def createChild(
        self, name: str, current: Ice.Current = None
    ) -> IceDrive.DirectoryPrx:
        """Create a new child directory and returns its proxy."""
        if self.user.isAlive() is True:
            if self.childs.get(name) is not None:
                raise IceDrive.ChildAlreadyExists
            child_directory = Directory(
                "/" + name, user_name=self.user_name, user=self.user
            )
            child_directory.parent = self
            self.childs["/" + name] = child_directory
            user_data = self._load_user_data()
            user = self._get_user(user_data)

            if user:
                self._update_directory_info(user, name, self.name)
                self._save_user_data(user_data)

            return IceDrive.DirectoryPrx.uncheckedCast(
                current.adapter.addWithUUID(child_directory)
            )
        return None

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        """Remove the child directory with the given name if exists."""
        if self.user.isAlive() is True:
            child_directory = self.childs.get("/" + name)
            if child_directory:
                del self.childs["/" + name]
                user_data = self._load_user_data()
                user = self._get_user(user_data)
                if user:
                    user["directorios"] = [
                        d
                        for d in user.get("directorios", [])
                        if d["nombre"] != "/" + name
                    ]
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

    def linkFile(
        self, filename: str, blob_id: str, current: Ice.Current = None
    ) -> None:
        """Link a file to a given blob_id."""
        for blobprx in self.persistencia_discovery.get_blob_service_proxies():
            try:
                blobprx.link(blob_id)
            except ConnectionError as e:
                self.persistencia_discovery.remove_blob_service_proxies(blobprx)
                if len(self.persistencia_discovery.get_blob_service_proxies()) == 0:
                    raise IceDrive.TemporaryUnavailable("BlobService") from e

        if filename in self.files:
            raise IceDrive.FileAlreadyExists(filename)
        self.files[filename] = blob_id
        self._update_file_info(filename, blob_id)

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        """Unlink (remove) a filename from the current directory."""
        for blobprx in self.persistencia_discovery.get_blob_service_proxies():
            try:
                blobprx.unlink(self.files[filename])
            except ConnectionError as e:
                self.persistencia_discovery.remove_blob_service_proxies(blobprx)
                if len(self.persistencia_discovery.get_blob_service_proxies()) == 0:
                    raise IceDrive.TemporaryUnavailable("BlobService") from e

        if filename not in self.files:
            raise IceDrive.FileNotFound(filename)
        del self.files[filename]
        user_data = self._load_user_data()
        user = self._get_user(user_data)
        if user:
            for directorio_info in user.get("directorios", []):
                if directorio_info["nombre"] == self.name:
                    archivos = directorio_info.get("archivos", [])
                    archivos = [
                        archivo for archivo in archivos if archivo["nombre"] != filename
                    ]
                    directorio_info["archivos"] = archivos
        self._save_user_data(user_data)

    def getPath(self, current: Ice.Current = None) -> str:
        """Return the path of the directory."""
        if self.user.isAlive() is True:
            path = ""
            while self.parent is not None:
                path = self.parent.name + path
            return path
        return None


class DirectoryService(IceDrive.DirectoryService):
    """Implementation of the IceDrive.DirectoryService interface."""

    file_path = "user_data.json"
    persistencia_discovery = DiscoveryPersistence()

    def __init__(self, publicador):
        self.user_directories: List[str, Directory] = {}
        self.publicador = publicador
        self.expected_responses = {}

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
        return next(
            (usuario for usuario in usuarios if usuario["nombre"] == user), None
        )

    def remove_object_if_exists(
        self, nombreusuario, adapter: Ice.ObjectAdapter, identity: Ice.Identity
    ) -> None:
        """Remove an object from the adapter if exists."""
        if adapter.find(identity) is not None:
            adapter.remove(identity)
            self.create_user(nombreusuario)

        del self.expected_responses[identity]

    def prepare_amd_response_callback(
        self, nombreusuario, current: Ice.Current
    ) -> IceDrive.DirectoryQueryResponsePrx:
        """Prepare an Ice.Future object and send the query."""
        future = Ice.Future()
        response = DirectoryQueryResponse(future)
        prx = current.adapter.addWithUUID(response)
        query_response_prx = IceDrive.DirectoryQueryResponsePrx.uncheckedCast(prx)

        identity = query_response_prx.ice_getIdentity()
        self.expected_responses[identity] = future
        threading.Timer(
            5.0,
            self.remove_object_if_exists(nombreusuario,
            current.adapter, identity),
        ).start()
        return query_response_prx

    def getRoot(
        self, user: IceDrive.UserPrx, current: Ice.Current = None
    ) -> IceDrive.DirectoryPrx:
        """Return the proxy for the root directory of the given user."""

        for autprx in self.persistencia_discovery.get_authentication_proxies():
            if autprx.verifyUser(user):
                pass
            else:
                self.persistencia_discovery.remove_authentication_proxies(autprx)
            if len(self.persistencia_discovery.get_authentication_proxies()) == 0:
                raise IceDrive.TemporaryUnavailable("AuthenticationService")

        if user.isAlive() is True:
            username = user.getUsername()
            user_directory = self.user_directories.get(username)

            if not user_directory:
                if not self.does_user_exist(username):
                    query_response_prx = self.prepare_amd_response_callback(
                        current, username
                    )
                    self.publicador.rootDirectory(query_response_prx)
                    user_directory = self.get_root_directory_for_user(username, user)
                else:
                    user_directory = self.get_root_directory_for_user(username, user)
                    self.user_directories[username] = user_directory

        return IceDrive.DirectoryPrx.uncheckedCast(
            current.adapter.addWithUUID(user_directory)
        )

    def does_user_exist(self, user: str) -> bool:
        """Check if the user exists in the user data."""
        user_data = self._load_user_data()
        usuarios = user_data.get("usuarios", [])
        return any(usuario.get("nombre") == user for usuario in usuarios)

    def get_root_directory_for_user(self, user_name: str, userprx) -> Directory:
        """Get the root directory for the given user."""
        user_data = self._load_user_data()

        for usuario in user_data["usuarios"]:
            if usuario["nombre"] == user_name:
                root_directory_info = usuario["directorios"][0]
                root_directory = Directory(
                    root_directory_info["nombre"], user_name, userprx
                )
                return self.load_directory_info(
                    root_directory, usuario, user_name, userprx
                )
        return None

    def create_user(self, user: str) -> None:
        """Create a new user with the given username."""
        user_data = self._load_user_data()

        nuevo_usuario = {
            "nombre": user,
            "id": len(user_data.get("usuarios", [])) + 1,
            "directorios": [{"nombre": f"/{user}", "padre": None, "archivos": []}],
        }
        user_data.setdefault("usuarios", []).append(nuevo_usuario)

        self._save_user_data(user_data)

    def load_directory_info(
        self,
        directory: Directory,
        user_info: dict,
        user: str,
        userprx,
        is_root: bool = True,
    ) -> Directory:
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
                child_directory = Directory(item_name, user, userprx)
                child_directory.parent = directory
                directory.childs[item_name] = child_directory

                for archivo_info in item_archivos:
                    archivo_nombre = archivo_info["nombre"]
                    archivo_blobid = archivo_info["blobid"]
                    child_directory.files[archivo_nombre] = archivo_blobid

                self.load_directory_info(
                    child_directory, user_info, user, userprx, is_root=False
                )
        return directory

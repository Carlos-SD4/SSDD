"""Servant implementations for service discovery."""

import Ice

import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    """Si falla la conexion con alguno de los proxys eliminarlo de la lista"""

    def __init__(self, my_prx):
        self.my_prx = my_prx
        self.discovery_persistence = DiscoveryPersistence()

    def announceAuthentication(
        self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None
    ) -> None:
        """Receive an Authentication service announcement."""
        if prx not in self.discovery_persistence.get_authentication_proxies():
            self.discovery_persistence.set_authentication_proxies(prx)
            print(f"Received Authentication announcement: {prx.ice_toString()}")

    def announceDirectoryServicey(
        self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None
    ) -> None:
        """Receive a Directory service announcement."""

        if (
            prx not in self.discovery_persistence.get_directory_service_proxies()
            and prx != self.my_prx
        ):
            self.discovery_persistence.set_directory_service_proxies(prx)
            print(f"Received DirectoryService announcement: {prx.ice_toString()}")
        else:
            return None

    def announceBlobService(
        self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None
    ) -> None:
        """Receive a Blob service announcement."""
        if prx not in self.discovery_persistence.get_blob_service_proxies():
            self.discovery_persistence.set_blob_service_proxies(prx)
            print(f"Received BlobService announcement: {prx.ice_toString()}")


class DiscoveryPersistence:
    """Persistence class for service discovery."""

    authentication_proxies = []
    directory_service_proxies = []
    blob_service_proxies = []

    def get_authentication_proxies(self):
        return self.authentication_proxies

    def get_directory_service_proxies(self):
        return self.directory_service_proxies

    def get_blob_service_proxies(self):
        return self.blob_service_proxies

    def set_blob_service_proxies(self, prx):
        self.blob_service_proxies.append(prx)

    def set_directory_service_proxies(self, prx):
        self.directory_service_proxies.append(prx)

    def set_authentication_proxies(self, prx):
        self.authentication_proxies.append(prx)

    def remove_blob_service_proxies(self, prx):
        self.blob_service_proxies.remove(prx)

    def remove_directory_service_proxies(self, prx):
        self.directory_service_proxies.remove(prx)

    def remove_authentication_proxies(self, prx):
        self.authentication_proxies.remove(prx)

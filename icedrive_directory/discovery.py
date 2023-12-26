"""Servant implementations for service discovery."""

import Ice

import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    def __init__(self):

        self.authentication_proxies = []
        self.directory_service_proxies = []
        self.blob_service_proxies = []

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""

        self.authentication_proxies.append(prx)
        print(f"Received Authentication announcement: {prx.ice_toString()}")

    def announceDirectoryServicey(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive a Directory service announcement."""
        '''Mandar mi propio DirectoryServicePrx'''


        '''Controlar que no reciba mensajes mios'''
        if prx not in self.directory_service_proxies:
            self.directory_service_proxies.append(prx)
            print(f"Received DirectoryService announcement: {prx.ice_toString()}")

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive a Blob service announcement."""

        self.blob_service_proxies.append(prx)
        print(f"Received BlobService announcement: {prx.ice_toString()}")

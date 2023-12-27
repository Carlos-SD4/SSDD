"""Servant implementations for service discovery."""

import Ice

import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    def __init__(self,my_prx):
        self.my_prx = my_prx
        self.authentication_proxies = []
        self.directory_service_proxies = []
        self.blob_service_proxies = []

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        if prx not in self.authentication_proxies:
            self.authentication_proxies.append(prx)
            print(f"Received Authentication announcement: {prx.ice_toString()}")

    def announceDirectoryServicey(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive a Directory service announcement."""

        if prx not in self.directory_service_proxies and prx != self.my_prx:
            self.directory_service_proxies.append(prx)
            print(f"Received DirectoryService announcement: {prx.ice_toString()}")

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive a Blob service announcement."""
        if prx not in self.blob_service_proxies:
            self.blob_service_proxies.append(prx)
            print(f"Received BlobService announcement: {prx.ice_toString()}")

"""Authentication service application."""

import logging
import sys
from typing import List

import Ice

from .directory import DirectoryService

class DirectoryApp(Ice.Application):
    """Implementation of the Ice.Application for the Directory service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the DirectoryApp class."""
        adapter = self.communicator().createObjectAdapter("DirectoryAdapter") 

        directory_service_impl = DirectoryService()

        directory_service_proxy = adapter.addWithUUID(directory_service_impl)
        adapter.activate() 

        logging.info("DirectoryService Proxy: %s", directory_service_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0

def main():
    """Handle the icedrive-directory program."""
    app = DirectoryApp()
    return app.main(sys.argv)

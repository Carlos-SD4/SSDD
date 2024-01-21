"""Authentication service application."""

import logging
import sys
from typing import List
import IceStorm
import Ice
from .discovery import Discovery, DiscoveryPersistence
from .directory import DirectoryService
import threading
import time
import IceDrive


class DirectoryApp(Ice.Application):
    def get_topic_manager(self):
        key = "IceStorm.TopicManager.Proxy"
        proxy = self.communicator().propertyToProxy(key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def publish_service(self, publicador, directory_proxy):
        try:
            publicador.announceDirectoryService(directory_proxy)
            threading.Timer(
                5.0, self.publish_service, (publicador, directory_proxy)
            ).start()
            print("Publicado")
        except Ice.CommunicatorDestroyedException:
            print("Comunicator destruido")

    def run(self, args: List[str]) -> int:
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print("Invalid proxy")
            return 2

        topic_name = "discovery"
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)
        publicador = IceDrive.DiscoveryPrx.uncheckedCast(topic.getPublisher())

        directory_topic_name = "directory"
        try:
            directory_topic = topic_mgr.retrieve(directory_topic_name)
        except IceStorm.NoSuchTopic:
            directory_topic = topic_mgr.create(directory_topic_name)
        publicadordirectory = directory_topic.getPublisher()

        adapter = self.communicator().createObjectAdapter("DirectoryAdapter")

        directory_service_impl = DirectoryService(publicadordirectory)
        directory_service_proxy = adapter.addWithUUID(directory_service_impl)
        adapter.activate()

        logging.info("DirectoryService Proxy: %s", directory_service_proxy)

        discovery = Discovery(directory_service_proxy)
        discovery_prx = adapter.addWithUUID(discovery)
        qos = {}
        topic.subscribeAndGetPublisher(qos, discovery_prx)

        directory_topic.subscribeAndGetPublisher(qos, discovery_prx)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(
            directory_service_proxy
        )
        self.publish_service(publicador, directory_service)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


def main():
    app = DirectoryApp()
    return app.main(sys.argv)

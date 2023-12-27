"""Authentication service application."""

import logging
import sys
from typing import List
import IceStorm
import Ice
from  IceDrive import Discovery
from .directory import DirectoryService
import threading
import time

class DirectoryApp(Ice.Application):
    """Implementation of the Ice.Application for the Directory service."""

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def publish_directory_service_periodically(self, directory_service_proxy, directory_topic, interval=5):
        while True:
            try:
                directory_topic.publish(qos={}, handle=directory_service_proxy)
                logging.info("DirectoryService Proxy republished: %s", directory_service_proxy)
            except Ice.Exception as ex:
                logging.error("Error republishing DirectoryService Proxy: %s", str(ex))

            time.sleep(interval)

    def run(self, args: List[str]) -> int:
        """Execute the code for the DirectoryApp class."""
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print('Invalid proxy')
            return 2
        topic_name = "Discovery"
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)
        publicador = topic.getPublisher()
        discovery = Discovery()
        discovery_prx = adapter.addWithUUID(discovery)

        qos ={}
        publicador.subscribeAndGetPublisher(qos, discovery_prx)

        directory_topic_name = "DirectoryService"
        try:
            directory_topic = topic_mgr.retrieve(directory_topic_name)
        except IceStorm.NoSuchTopic:
            directory_topic = topic_mgr.create(directory_topic_name)
        directory_topic.subscribeAndGetPublisher(qos, discovery_prx)


        authentication_topic_name = "Authentication"
        try:
            authentication_topic = topic_mgr.retrieve(authentication_topic_name)
        except IceStorm.NoSuchTopic:
            authentication_topic = topic_mgr.create(authentication_topic_name)
        authentication_topic.subscribeAndGetPublisher(qos, discovery_prx)


        blob_topic_name = "BlobService"
        try:
            blob_topic = topic_mgr.retrieve(blob_topic_name)
        except IceStorm.NoSuchTopic:
            blob_topic = topic_mgr.create(blob_topic_name)
        blob_topic.subscribeAndGetPublisher(qos, discovery_prx)



        adapter = self.communicator().createObjectAdapter("DirectoryAdapter")

        directory_service_impl = DirectoryService()

        directory_service_proxy = adapter.addWithUUID(directory_service_impl)
        adapter.activate()

        logging.info("DirectoryService Proxy: %s", directory_service_proxy)

        publish_thread = threading.Thread(
            target=self.publish_directory_service_periodically,
            args=(directory_service_proxy, directory_topic),
            daemon=True
        )
        publish_thread.start()

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        directory_topic.unsubscribe(discovery_prx)
        authentication_topic.unsubscribe(discovery_prx)
        blob_topic.unsubscribe(discovery_prx)

        return 0

def main():
    """Handle the icedrive-directory program."""
    app = DirectoryApp()
    return app.main(sys.argv)

# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rclpy.impl.implementation_singleton import rclpy_implementation as _rclpy

from rclpy.client import Client
from rclpy.exceptions import NoTypeSupportImportedException
from rclpy.publisher import Publisher
from rclpy.qos import qos_profile_default, qos_profile_services_default
from rclpy.service import Service
from rclpy.subscription import Subscription


class Node:

    def __init__(self, handle):
        self.clients = []
        self.handle = handle
        self.publishers = []
        self.services = []
        self.subscriptions = []

    def create_publisher(self, msg_type, topic, qos_profile=qos_profile_default):
        # this line imports the typesupport for the message module if not already done
        if msg_type.__class__._TYPE_SUPPORT is None:
            msg_type.__class__.__import_type_support__()
        if msg_type.__class__._TYPE_SUPPORT is None:
            raise NoTypeSupportImportedException
        publisher_handle = _rclpy.rclpy_create_publisher(
            self.handle, msg_type, topic, qos_profile.get_c_qos_profile())
        publisher = Publisher(publisher_handle, msg_type, topic, qos_profile, self.handle)
        self.publishers.append(publisher)
        return publisher

    def create_subscription(self, msg_type, topic, callback, qos_profile=qos_profile_default):
        # this line imports the typesupport for the message module if not already done
        if msg_type.__class__._TYPE_SUPPORT is None:
            msg_type.__class__.__import_type_support__()
        if msg_type.__class__._TYPE_SUPPORT is None:
            raise NoTypeSupportImportedException
        [subscription_handle, subscription_pointer] = _rclpy.rclpy_create_subscription(
            self.handle, msg_type, topic, qos_profile.get_c_qos_profile())

        subscription = Subscription(
            subscription_handle, subscription_pointer, msg_type,
            topic, callback, qos_profile, self.handle)
        self.subscriptions.append(subscription)
        return subscription

    def create_client(self, srv_type, srv_name, qos_profile=qos_profile_services_default):
        if srv_type.__class__._TYPE_SUPPORT is None:
            srv_type.__class__.__import_type_support__()
        if srv_type.__class__._TYPE_SUPPORT is None:
            raise NoTypeSupportImportedException
        [client_handle, client_pointer] = _rclpy.rclpy_create_client(
            self.handle,
            srv_type,
            srv_name,
            qos_profile.get_c_qos_profile())
        client = Client(
            self.handle, client_handle, client_pointer, srv_type, srv_name, qos_profile)
        self.clients.append(client)
        return client

    def create_service(
            self, srv_type, srv_name, callback, qos_profile=qos_profile_services_default):
        if srv_type.__class__._TYPE_SUPPORT is None:
            srv_type.__class__.__import_type_support__()
        if srv_type.__class__._TYPE_SUPPORT is None:
            raise NoTypeSupportImportedException
        [service_handle, service_pointer] = _rclpy.rclpy_create_service(
            self.handle,
            srv_type,
            srv_name,
            qos_profile.get_c_qos_profile())
        service = Service(
            self.handle, service_handle, service_pointer,
            srv_type, srv_name, callback, qos_profile)
        self.services.append(service)
        return service

    def destroy_publisher(self, publisher):
        for pub in self.publishers:
            if pub.publisher_handle == publisher.publisher_handle:
                _rclpy.rclpy_destroy_node_entity(
                    'publisher', pub.publisher_handle, self.handle)
                self.publishers.remove(pub)
                return True
        return False

    def destroy_subscription(self, subscription):
        for sub in self.subscriptions:
            if sub.subscription_handle == subscription.subscription_handle:
                _rclpy.rclpy_destroy_node_entity(
                    'subscription', sub.subscription_handle, self.handle)
                self.subscriptions.remove(sub)
                return True
        return False

    def destroy_service(self, service):
        for srv in self.services:
            if srv.service_handle == service.service_handle:
                _rclpy.rclpy_destroy_node_entity(
                    'service', srv.service_handle, self.handle)
                self.services.remove(srv)
                return True
        return False

    def destroy_client(self, client):
        for cli in self.clients:
            if cli.client_handle == client.client_handle:
                _rclpy.rclpy_destroy_node_entity(
                    'client', cli.client_handle, self.handle)
                self.clients.remove(cli)
                return True
        return False

    def destroy_node(self):
        for sub in self.subscriptions:
            _rclpy.rclpy_destroy_node_entity(
                'subscription', sub.subscription_handle, self.handle)
        for pub in self.publishers:
            _rclpy.rclpy_destroy_node_entity('publisher', pub.publisher_handle, self.handle)
        for cli in self.clients:
            _rclpy.rclpy_destroy_node_entity('client', cli.client_handle, self.handle)
        for srv in self.services:
            _rclpy.rclpy_destroy_node_entity('service', srv.service_handle, self.handle)
        _rclpy.rclpy_destroy_entity('node', self.handle)
        self.handle = None

    def get_topic_names_and_types(self):
        return _rclpy.rclpy_get_topic_names_and_types(self.handle)

    def __del__(self):
        if self.handle is not None:
            self.destroy_node()
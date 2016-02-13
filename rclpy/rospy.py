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

import sys
import time
import rclpy

global_node = None
global_node_name = ''
global_pending_publishers = []
global_pending_subscribers = []

def init_node(name, anonymous=True):
    global global_node, global_node_name, global_pending_publishers, global_pending_subscribers
    if global_node:
        raise Exception('Node already created; did you already call init_node()?')
    rclpy.init(sys.argv)
    # TODO: do something with anonymous
    global_node = rclpy.create_node(name)
    global_node_name = name
    for p in global_pending_publishers:
        p.create(global_node)
    global_pending_publishers = []
    for s in global_pending_subscribers:
        s.create(global_node)
    global_pending_subscribers = []

def is_shutdown():
    return not rclpy.ok()

def get_time():
    return time.time()

def spin():
    global global_node
    if not global_node:
        raise Exception('No node; did you call init_node()?')
    rclpy.spin(global_node)

def get_caller_id():
    global global_node_name
    return global_node_name

def logdebug(msg, *args):
    output = msg
    for a in args:
        output += ' ' + str(a)
    print('[DEBUG] ' + output)

def loginfo(msg, *args):
    output = msg
    for a in args:
        output += ' ' + str(a)
    print('[INFO] ' + output)

def logwarn(msg, *args):
    output = msg
    for a in args:
        output += ' ' + str(a)
    print('[WARN] ' + output)

def logerr(msg, *args):
    output = msg
    for a in args:
        output += ' ' + str(a)
    print('[ERROR] ' + output)

def logfatal(msg, *args):
    output = msg
    for a in args:
        output += ' ' + str(a)
    print('[FATAL] ' + output)

class Publisher:
    def __init__(self, topic, topictype, queue_size=10):
        self.topic = topic
        self.topictype = topictype
        self.queue_size = queue_size
        self.pub = None
        self.node = None

        global global_node, global_pending_publishers
        if global_node:
            self.pub = self.create(global_node)
        else:
            global_pending_publishers.append(self)

    def create(self, node):
        if self.pub:
            raise Exception('Publisher already created.')
        self.node = node
        from rclpy.qos import qos_profile_default
        # TODO: insert queue_size somewhere in qos
        self.pub = self.node.create_publisher(
          self.topictype, self.topic, qos_profile_default)

    def publish(self, msg):
        if not self.pub:
            raise Exception('Publisher not created; did you call init_node?')
        self.pub.publish(msg)

class Subscriber:
    def __init__(self, topic, topictype, callback):
        self.topic = topic
        self.topictype = topictype
        self.callback = callback
        self.sub = None
        self.node = None

        global global_node, global_pending_subscribers
        if global_node:
            self.sub = self.create(global_node)
        else:
            global_pending_subscribers.append(self)

    def create(self, node):
        if self.sub:
            raise Exception('Subscriber already created.')
        self.node = node
        from rclpy.qos import qos_profile_default
        # TODO: insert queue_size somewhere in qos
        self.sub = self.node.create_subscription(
          self.topictype, self.topic, self.callback, qos_profile_default)

class Rate:
    def __init__(self, period):
        self.period = period

    def sleep(self):
        time.sleep(1/self.period)

class ROSInterruptException(Exception):
    pass

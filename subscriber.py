#!/usr/bin/env python3

#   Copyright (c) 2023 Liav A
#   
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import argparse
import random
import femtosip
import logging
from paho.mqtt import client as mqtt_client
from systemd.journal import JournalHandler

def mqtt_subscribe(mqtt_topic, sip_connection, extension_number, sip_call_duration, client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        sip_connection.call(extension_number, sip_call_duration)

    client.subscribe(mqtt_topic)
    client.on_message = on_message

def connect_mqtt(broker_ip, broker_port, broker_username, broker_password, client_id) -> mqtt_client:
    log = logging.getLogger('pymqtt-sip-doorbell-subscriber')
    log.addHandler(JournalHandler())
    log.setLevel(logging.INFO)
    def on_disconnect(client, userdata, rc):
        log.info("Exit due to disconnecting from MQTT Broker, reason: " + str(rc))
        exit(1)
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")
            log.info("Exit due to connection failure to MQTT Broker, reason: " + str(rc))
            exit(1)

    client = mqtt_client.Client(client_id)
    if broker_username is not None and broker_password is not None:
        client.username_pw_set(broker_username, broker_password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker_ip, broker_port)
    return client

def main():
    parser = argparse.ArgumentParser(
        description='A microscopic SIP client that can be used to ring a ' + 
                    'phone.')
    parser.add_argument('--sip-gateway', required=True,
        help='Hostname or IP address of the SIP server')
    parser.add_argument('--sip-gateway-port', default=5060, type=int,
        help='Port of the SIP server (default 5060)')
    parser.add_argument('--sip-user', required=True,
        help='Username used for authentication at the SIP server')
    parser.add_argument('--sip-password', default='',
        help='Password used in conjunction with the user for authentication ' +
             'at the SIP server. (default '')')
    parser.add_argument('--sip-displayname', default=None,
        help='Alter the displayed caller name. (defaults to SIP configuration)')
    parser.add_argument('--sip-transport-protocol', default="tcp", 
        help='supported protocols: IPv4: udp/tcp, IPv6: udp6/tcp6')
    parser.add_argument('--extension-number', required=True,
        help='Phone number of the endpoint that will be called')
    parser.add_argument('--call-duration', default=15.0, type=float,
        help='Pause in seconds until the call is canceled (default 15.0)')
    parser.add_argument('--sip-respond-timeout', default=1.0, type=float,
        help='Period in seconds the SIP server must respond within (default 1.0)')
    parser.add_argument('--mqtt-broker-ip', required=True,
        help='MQTT Broker IP')
    parser.add_argument('--mqtt-broker-port', default=1883, type=int,
        help='MQTT Broker TCP port')
    parser.add_argument('--mqtt-topic', required=True,
        help='MQTT Broker topic to be subscribed')
    parser.add_argument('--mqtt-user', default=None,
        help='MQTT Broker username')
    parser.add_argument('--mqtt-password', default=None,
        help='MQTT Broker username')

    args = parser.parse_args()

    client_id = f'python-mqtt-{random.randint(0, 65536)}'
    client = connect_mqtt(args.mqtt_broker_ip, args.mqtt_broker_port, args.mqtt_user, args.mqtt_password, client_id)
    sip = femtosip.SIP(args.sip_user, args.sip_password, args.sip_gateway, args.sip_gateway_port, args.sip_displayname)
    mqtt_subscribe(args.mqtt_topic, sip, args.extension_number, args.call_duration, client)
    client.loop_forever()

if __name__ == '__main__':
    main()

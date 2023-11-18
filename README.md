# MQTT SIP Doorbell Subscriber ‒ A minimal SIP client with MQTT client for doorbell usage

*MQTT-SIP-Doorbell-Subscriber* is a minimal Python solution that integrates FemtoSIP
and paho-mqtt for creating an MQTT subscriber client, that triggers a SIP
call on receiving notifications from a subscribed MQTT broker with a specified topic.

## How to use

```sh
git clone https://github.com/supercomputer7/mqtt-sip-doorbell-subscriber
cd mqtt-sip-doorbell-subscriber

# Execute the MQTT subscriber script
python3 subscriber.py \ 
    --mqtt-broker-ip 192.168.1.1 \
    --mqtt-topic doorbell \
    --mqtt-user MQTT_USER \
    --mqtt-password MQTT_PASS \
    --sip-gateway 192.168.1.1 \
    --sip-user SIP_USER \
    --sip-password SIP_PASSWORD \
    --extension-number SIP_EXTENSION \
    --sip-displayname "GO CHECK THE DOOR"
```

If everything works, you should get an output which looks like this:
```
Connected to MQTT Broker!
```

You can use this Python script as a `systemd` service with the provided
`mqtt-sip-doorbell-subscriber.service` file. Please configure the script as desired by
editing the service file. Then install the service by running the following
commands:
```sh
sudo mkdir -p /opt/mqtt_sip_doorbell_subscriber/
sudo install femtosip.py subscriber.py /opt/mqtt_sip_doorbell_subscriber
sudo install mqtt-sip-doorbell-subscriber.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable mqtt-sip-doorbell-subscriber.service
sudo systemctl start mqtt-sip-doorbell-subscriber.service
```

## License

The `femtosip.py` code is subject to the GNU Affero General Public License.
Anything else in the project is licensed under the MIT license

## Personal note

This is basically a relay between an MQTT subscribed notifications channel
to initiating SIP calls. The original intent is for IoT home doorbell device which is created
with an ESP32 MCU that sends notifications over the MQTT protocol, so it could trigger
a SIP call to an extension (or maybe multiple extensions!) with this script which is running
on another linux machine.

However, it could be used for any other home automation that should initiate a SIP call,
as you can imagine. If you find this useful in some way, then I am genuinely interested to hear what
you do with this and how this code could be improved! :)

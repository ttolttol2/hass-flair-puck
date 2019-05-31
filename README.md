Home Assistant Custom Component for Flair Puck
==============================================
see https://flair.co for details of this smart device control system.
Tested on raspberry pi 3B+, **no guarantees** on anything else!
``` 
arch            armv7l
dev             false
docker          false
hassio          false
os_name         Linux
python_version  3.5.3
timezone        Asia/Seoul
version         0.93.2
virtualenv      true
```
## Introduction
This program has the following features:
* Read all flair puck values
* Use room temperature of a puck as state of HA entitiy
* Use sensing info(date,humidity,light,room pressure) as attribute of HA entitiy
* ~~Set puck values (room occupied, set_point_c, clear hold)~~
* ~~auto timezone correction of time/dates~~
## Pre-Requisites
To use this program, you will need to have requested access to the Flair API (email hello@flair.co) you will get:

* CLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
* CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

You will also need to know your home_id - this is a number (usually 4 digits) identifying your home.
In the Flair web page showing your devices, it's usually the number at the end of the URL. eg https://my.flair.co/h/1234 where 1234 is your home id.
**you can find puck's name also.**
## Install & Configure
Make sure you have the Flair API Client installed (https://github.com/flair-systems/flair-api-client-py)

```
pip install git+git://github.com/flair-systems/flair-api-client-py.git
```
copy all the files into the Home Assistant location. It can now be installed either to the custom_components folder
```bash
$ cd /tmp
$ git clone https://github.com/ttolttol2/hass-flair-puck.git
$ cp hass-flair-puck ~/.homeassistant/custom_components/flair
$ ls ~/.homeassistant/custom_components/flair
README.md  __init__.py  manifest.json  sensor.py
```
In your configuration.yaml:
```yaml
sensor:
  - platform: flair
    client_id: YOUR_CLIENT_ID
    client_secret: YOUR_CLIENT_SECRET
    home_id: YOUR_HOME_ID
    scan_interval: 60
    name: YOUR_PUCK_NAME
    monitored_conditions:
      - temperature
      - light
      - humidity
```
Restart the Home Assistant services.
Now you can use puck's sensing data on the hass frontend.
```
#like this
sensor.puck_10fl_458b_temperature
sensor.puck_10fl_458b_light
sensor.puck_10fl_458b_humidity
```
```json
10fl-c5a3: {
  "online": false
}
10fl-458b: {
  "Pressure": 100.27,
  "light": 288,
  "date": "2019-05-31T06:39:30.958266+00:00",
  "Temperature": 25.24,
  "Humidity": 49
}
```

""" flair sensor """

import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_NAME, CONF_UNIT_OF_MEASUREMENT
from flair_api import make_client
import time

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, descovery_info=None):
    """Setup the sensor platform"""
    name = config.get(CONF_NAME)
    unit = config.get(CONF_UNIT_OF_MEASUREMENT)
    client_id = config.get('client_id')
    client_secret = config.get('client_secret')
    home_id = config.get('home_id')

    add_entities([FlairPuck(name, unit, client_id, client_secret, home_id)])
    return

def GetPuckData(client, home_id):
    st = client.get("structures", id=home_id)
    pucks = st.get_rel('pucks')
    #print("got data for %d pucks" % len(pucks))
    puck_data = {}
    for puck in pucks:
        if puck.attributes['current-rssi'] == None:
            puck_data[puck.attributes['name']] = {'online':False}
        else:
            sr = puck.get_rel('sensor-readings')
            #print("got data for %d sensor-readings" % len(sensor_readings))
            puck_data[puck.attributes['name']] = { 'date':sr[0].attributes['created-at'],
                'Pressure':sr[0].attributes['room-pressure'],
                'Humidity':sr[0].attributes['humidity'],
                'light':sr[0].attributes['light'],
                'Temperature':sr[0].attributes['room-temperature-c']
            }
    return puck_data

class FlairPuck(Entity):
    def __init__(self, name, unit, client_id, client_secret, home_id):
        _LOGGER.info("initialize Flair Puck Sensor Data")
        self._name = '{} {}'.format('flair_puck', name)
        self._puck_name = name
        self._unit_of_measurement = unit
        self._state = None
        self._puck_data = {}
        self._home_id = home_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._client = make_client(client_id, client_secret, 'https://api.flair.co')
        self._expiry_time = time.time() + self._client.expires_in

    @property
    def name(self):
        return self._name
    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def state(self):
        return self._state

    @property
    def state_attributes(self):
        return self._puck_data

    def update(self):
        _LOGGER.info("fetch new state data for the flair puck")
        self._puck_data = GetPuckData(self._client, self._home_id)
        self._state = self._puck_data[self._puck_name]['Temperature']

        _LOGGER.info("Authentication expires in: %ds" % int(self._expiry_time - time.time()))
        if int(self._expiry_time - time.time()) < 120: #second
            #refresh session
            self._client = make_client(self._client_id, self._client_secret, 'https://api.flair.co')
            self._expiry_time = time.time() + self._client.expires_in


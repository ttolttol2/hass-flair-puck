""" flair sensor """

import logging
import time
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_MONITORED_CONDITIONS)
from flair_api import make_client

CONF_CLIENT_ID = 'client_id'
CONF_CLIENT_SECRET = 'client_secret'
CONF_HOME_ID = 'home_id'

_LOGGER = logging.getLogger(__name__)
_MONITORED_CONDITIONS = {
    'temperature': ['Temperature', 'Value', '°C', 'mdi:temperature-celsius'],
    'light': ['light', 'Value', 'Lux', 'mdi:theme-light-dark'],
    'humidity': ['Humidity', 'Value', '%', 'mdi:thermometer']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CLIENT_ID): cv.string,
    vol.Required(CONF_CLIENT_SECRET): cv.string,
    vol.Required(CONF_HOME_ID): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS):
        vol.All(cv.ensure_list, [vol.In(_MONITORED_CONDITIONS)]),
})

def setup_platform(hass, config, add_entities, descovery_info=None):
    """Setup the sensor platform"""
    name = config.get(CONF_NAME)
    client_id = config.get(CONF_CLIENT_ID)
    client_secret = config.get(CONF_CLIENT_SECRET)
    home_id = config.get(CONF_HOME_ID)
    monitored_conditions = config.get(CONF_MONITORED_CONDITIONS)

    sensors = []
    if monitored_conditions is not None:
        for item in monitored_conditions:
            sensors += [FlairPuck(
                    name, client_id, client_secret, home_id, _MONITORED_CONDITIONS[item])]

    add_entities(sensors, True)
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
    def __init__(self, name, client_id, client_secret, home_id, item_info):
        _LOGGER.info("initialize Flair Puck Sensor Data")
        self.home_id = home_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.client = make_client(client_id, client_secret, 'https://api.flair.co')
        self.expiry_time = time.time() + self.client.expires_in
        self.puck_name = name
        self.puck_data = {}
        self.item_name = item_info[0]
        self.item_type = item_info[1]
        self.item_unit = item_info[2]
        self.item_icon = item_info[3]
        self.item_state = ''
        self._name = '{} {} {}'.format('puck', name, self.item_name)

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self.item_icon

    @property
    def unit_of_measurement(self):
        return self.item_unit

    @property
    def state(self):
        return self.item_state

    @property
    def state_attributes(self):
        return self.puck_data

    def update(self):
        _LOGGER.info("fetch new state data for the flair puck")
        self.puck_data = GetPuckData(self.client, self.home_id)
        self.item_state = self.puck_data[self.puck_name][self.item_name]

        _LOGGER.info("Authentication expires in: %ds" % int(self.expiry_time - time.time()))
        if int(self.expiry_time - time.time()) < 120: #second
            #refresh session
            self.client = make_client(self.client_id, self.client_secret, 'https://api.flair.co')
            self.expiry_time = time.time() + self.client.expires_in


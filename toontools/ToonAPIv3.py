"""Python library for interacting with Toon API"""
import json
import logging

import requests
import certifi

import urllib3
import urllib

import time


STATENAMES = [
    "Comfort",
    "Home",
    "Sleeping",
    "Away",
    "Holiday",
    "tempoff"
]


def msec_to_time(msec):
    '''Convert miliseconds to Python datetime object'''

    date_time = time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(msec/1000.0)
    )
    return(date_time)


class Toon:
    """ Log in to the Toon API, and do stuff. """

    def __init__(self, username, password, client_id, client_secret,
                 tenant_id, redirect_uri="http://fake.url", **kwargs):
        '''Initialise API session and helper variables'''
        self._agreement_id = None

        self.host = kwargs.get('host', 'api.toon.eu')
        self.api_version = kwargs.get('api_version', 'v3')
        self.max_retries = 3
        self.retry_interval = 1

        self.apiurl = "https://{}/toon/{}".format(
            self.host, self.api_version
        )

        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id  # TODO: Check for valid values
        self.redirect_uri = redirect_uri

        self.toonapi = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()
        )
        logging.debug("CertTest is done")

        self._session = requests.session()
        self._session.headers.update(
            {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            }
        )

        self._authenticate()

    @classmethod
    def load_from_config(cls, filename='conf/toon.json'):
        """Initialise Toon class from configuration file"""

        with open(filename) as data_file:
            configuration = json.load(data_file)

        username = configuration['connectioninfo']['username']
        password = configuration['connectioninfo']['password']
        client_id = configuration['connectioninfo']['consumerkey']
        client_secret = configuration['connectioninfo']['consumersecret']
        redirect_uri = configuration['connectioninfo']['redirect_uri']
        tenant_id = configuration['connectioninfo']['tenant_id']

        return cls(
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            redirect_uri=redirect_uri
        )

    def _get(self, endpoint, payload=None):
        """Perform HTTP GET request against Toon API"""
        url = "{}/{}".format(self.apiurl, endpoint)

        if payload is not None:
            #response = self._session.get(url, json.dumps(payload))
            response = self._session.get(url, params=payload)
        else:
            response = self._session.get(url)

        if response.status_code != requests.codes.ok:
            raise IOError(
                'HTTP GET {} failed ({}). response: {}'.format(
                    url,
                    response.status_code,
                    response.text
                )
            )

        try:
            return response.json()
        except ValueError:
            return response.text

    def _post(self, endpoint, payload=None):
        """Perform HTTP POST request against Toon API"""
        url = "{}/{}".format(self.apiurl, endpoint)

        if payload is not None:
            response = self._session.post(url, params=payload)
        else:
            response = self._session.post(url)

        if response.status_code != requests.codes.ok:
            raise IOError(
                'HTTP POST {} failed ({}). response: {}'.format(
                    url,
                    response.status_code,
                    response.text
                )
            )

        try:
            return response.json()
        except ValueError:
            return response.text


    def _put(self, endpoint, payload=None):
        """Perform HTTP POST request against Toon API"""
        url = "{}/{}".format(self.apiurl, endpoint)

        if payload is not None:
            response = self._session.put(url, data=payload)
        else:
            response = self._session.put(url)

        if response.status_code != requests.codes.ok:
            raise IOError(
                'HTTP PUT {} failed ({}). response: {}'.format(
                    url,
                    response.status_code,
                    response.text
                )
            )

        try:
            return response.json()
        except ValueError:
            return response.text

    def _authenticate(self):
        """(re)authenticate against Toon API"""
        logging.info("Authenticate Application to Toon Webform")

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # self.client_id = '5DXjEsAC5fYOLX18iqzUtWEJgJ6dfiVu'
        # Retrieve API Code using username/password
        params = {
            'username': self.username,
            'password': self.password,
            'response_type': 'code',
            'tenant_id': self.tenant_id,
            'client_id': self.client_id,
            'state': '',
            'scope': ''
        }

        # if authenticated succesfully this will do a redirect
        # to our fake callback url. We grab the code from
        # the redirect url and use it to retrieve our token
        url = 'https://{}/authorize/legacy'.format(self.host)
        response = requests.post(url, data=params, headers=headers)
        
        parsed_url = urllib.parse.urlparse(response.url)
        code = urllib.parse.parse_qs(parsed_url.query)['code'][0]
        logging.debug('Retrieved code: {}'.format(code))

        # Retrieve token
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code
        }

        url = 'https://{}/token'.format(self.host)
        response = requests.post(url, data=payload, headers=headers)

        if response.status_code != requests.codes.ok:
            raise IOError(
                'HTTP POST {} failed ({}). response: {}'.format(
                    response.url,
                    response.status_code,
                    response.text
                )
            )

        data = response.json()

        self.token = data['access_token']

        # TODO: check token expiry date and before each 
        # http call check if we need to refresh
        # self.token_expires_at = datetime + data['expires_in']
        # self.refresh_token = data['refresh_token']

        auth_header = {
            'Authorization': 'Bearer {}'.format(self.token)
        }
        self._session.headers.update(auth_header)

    @property
    def agreement_id(self):
        """returns the agreement ID, if not set query Toon API"""
        if self._agreement_id is None:

            response = self._get('agreements')
            try:
                self._agreement_id = response[0]['agreementId']
            except IndexError or KeyError:
                raise IOError(
                    'Could not retrieve AgreementID: {}'.format(response)
                )

        return self._agreement_id

    def get_status(self):
        """Getting complete Toon status"""
        logging.info("Getting Toon Status:")
        endpoint = "{}/status".format(self.agreement_id)

        status = self._get(endpoint)
        logging.info("Current Setpoin: {}, Current Temp: {}".format(status["thermostatInfo"]["currentSetpoint"]/100, status["thermostatInfo"]["currentDisplayTemp"]/100))
        return status

    def get_thermostat_states(self):
        """Getting all states with value"""
        logging.info("Getting States:")

        uri = "{}/thermostat/states".format(self.agreement_id)

        states = self._get(uri)

        for state in states['state']:
            state["name"] = STATENAMES[int(state["id"])]
            logging.info(
                "{} is set to {} C".format(
                    state["name"],
                    state["tempValue"]/100
                )
            )

        return states

    def get_thermostat_state_current(self):
        """Retrieves current thermostat state"""

        logging.info("Getting Current state:")

        uri = "{}/thermostat".format(self.agreement_id)

        current_state = self._get(uri)

        logging.info("Current Setpoint:     {}C".format(
            int(current_state["currentSetpoint"])/100)
        )
        logging.info("Current Temperature:  {}C".format(
            int(current_state["currentDisplayTemp"])/100
        ))
        logging.info("Current Prog State:   {}".format(
            current_state["programState"]
        ))
        logging.info("Current State in Prg: {}".format(
            STATENAMES[(current_state["activeState"])]
        ))
        logging.info("Next State in Prog:   {}".format(
            STATENAMES[int(current_state["nextState"])]
        ))
        logging.info("Changing at: {}  sec".format(
            (int(current_state["nextTime"]))
        ))
        logging.info("Changing at: {}  ".format(
            (msec_to_time(current_state["nextTime"]*1000))
        ))
        logging.info("Next Temp:            {}C".format(
            (int(current_state["nextSetpoint"])/100)
        ))
        logging.info("Real Setpoint:        {}C".format(
            (int(current_state["realSetpoint"])/100)
        ))

        return current_state

    def get_thermostat_programs(self):
        """Retrieve all available thermostat programs"""

        logging.info("Getting Thermostat Programs")

        uri = "{}/thermostat/programs".format(self.agreement_id)
        return self._get(uri)

    def get_thermostat_current_temp(self):
        """Retrieve current Thermostat temperature in degrees C"""

        logging.info("Getting Thermostat Current Temp")

        uri = "{}/thermostat".format(self.agreement_id)
        response = self._get(uri)

        current_temp = int(response["currentSetpoint"])/100
        return current_temp

    def get_cons_elec_gas(self, interval='hours',
                          from_time=1514761200000,
                          to_time=(int(time.time())*1000),
                          gas_elec='gas'):
        """
        Get data from 2018-01-01 00:00:00 till now
        give from and to time in msec
        give gas_elec: "gas|electricity"
        response is like:
        {
            u'hours': [
                {
                    u'timestamp': 1514761200000,
                    u'peak': 0.0,
                    u'unit': u'Wh',
                    u'offPeak': 314.0
                },
                ...
            ],
            u'weeks': [],
            u'months': [],
            u'days': [],
            u'years': []
        }
        """
        logging.info("Getting Energy consumption: {} for {}, from {}, to {}".format(gas_elec, interval, from_time, to_time))

        uri = "{}/consumption/{}/data".format(
            self.agreement_id, gas_elec
        )
        payload = {
            'fromTime': from_time,
            'toTime': to_time,
            'interval': interval
        }

        response = self._get(uri, payload=payload)

        logging.debug("last usage from: {} to: {}\n with payload: {}\n {}".format(
            msec_to_time(int(payload["fromTime"])),
            msec_to_time(int(payload["toTime"])),
            payload,
            response
        ))

        return response

    def get_termostat_states(self):

        logging.info("Getting Thermostat states: ")

        uri = "{}/thermostat/states".format(
            self.agreement_id
        )

        payload = { }
        response = self._get(uri, payload=payload)
        logging.debug(response)

        return response

    def set_termostat_states(self, 
                             Comfort="2100",
                             Home="2000",
                             Sleeping="1500",
                             Away="1200",
                             Holiday="1600",
                             tempoff="600"):

        logging.info("Setting Thermostat states: ")

        uri = "{}/thermostat/states".format(
            self.agreement_id
        )

        payload = '''{ "state" : 
            [ 
              {"id" : "0","tempValue" : "''' + Comfort +  '''","dhw" : "1"},
              {"id" : "1","tempValue" : "''' + Home +     '''","dhw" : "1"},
              {"id" : "2","tempValue" : "''' + Sleeping + '''","dhw" : "1"},
              {"id" : "3","tempValue" : "''' + Away +     '''","dhw" : "1"},
              {"id" : "4","tempValue" : "''' + Holiday +  '''","dhw" : "1"},
              {"id" : "5","tempValue" : "''' + tempoff +   '''","dhw" : "1"} 
            ]
        }'''

        response = self._put(uri, payload=payload)
        
        return response

    def set_termostat_temp(self, state="2", temp="1600", prog="1"):

        logging.info("Setting Current Temp states: ")

        uri = "{}/thermostat".format(
            self.agreement_id
        )

        payload = '''{
                    "currentSetpoint": "''' + temp + '''",
                    "programState": "''' + prog + '''",
                    "activeState": "''' + state + '''"
                   }'''
        response = self._put(uri, payload=payload)
        return response

    def get_devices(self):
        """Retrieve all available devices and show states"""

        logging.info("Getting Devices")

        uri = "{}/devices".format(self.agreement_id)
        response = self._get(uri)
        for dev in response:
            logging.info("{} device type: {}, state: {}, uuid {}".format(dev['name'], dev['deviceType'], dev['currentState'], dev['uuid']))

        return response

    def get_device(self, devuuid):
        """Retrieve one  devices and show state"""

        logging.info("Getting Device: {}".format(devuuid))

        uri = "{}/devices/{}".format(self.agreement_id, devuuid)
        dev = self._get(uri)
        logging.info("{} device type: {}, state: {}".format(dev['name'], dev['deviceType'], dev['currentState'], dev['uuid']))

        return dev

    def set_device(self, devuuid, state='0'):
        """Set device state """

        logging.info("Setting Device: {}".format(devuuid))

        uri = "{}/devices/{}".format(
            self.agreement_id, 
            devuuid
        )

        payload = '''{
                    "uuid": "''' + devuuid + '''",
                    "currentState": "''' + state + '''"
                   }'''

        response = self._put(uri, payload=payload)
        return response




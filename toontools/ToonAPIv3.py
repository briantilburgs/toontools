"""Python library for interacting with Toon API"""
import json
import logging

import requests
import certifi
import urllib3

import time


STATENAMES = [
    "Comfort",
    "Home",
    "Sleeping",
    "Away",
    "Holiday?",
    "VeryCold?"
]


def msec_to_time(self, msec):
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
            response = self._session.get(url, data=json.dumps(payload))
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
            response = self._session.post(url)
        else:
            response = self._session.post(url, data=json.dumps(payload))

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

    def _authenticate(self):
        """(re)authenticate against Toon API"""
        logging.info("Authenticate Application to Toon Webform")

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Retrieve API Code using username/password
        params = {'username': self.username, 'password': self.password}
        url = 'https://{}/authorize'.format(self.host)
        response = self._session.get(url, params=params, headers=headers)
        print(response.text)
        exit()

        # Retrieve token
        payload = (
            "client_id={}"
            "&tenant_id={}"
            "&grant_type=authorization_code"
            "code={}".format(
                self.client_id, self.tenant_id, 'code'
            )
        )

        url = 'https://{}/token'.format(self.host)
        response = requests.post(url, data=payload, headers=headers)

        if response.status_code != requests.codes.ok:
            raise IOError(
                'HTTP POST {} failed ({}). response: {}'.format(
                    url,
                    response.status_code,
                    response.text
                )
            )

        token = response.text
        print(token)
        # TODO: parse 'expires_in' field and request new token if expired

        auth_header = {
            'Authorization': 'Bearer {}'.format(token)
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
        endpoint = "{}/status".format(self.agreemend_id)
        return self._get(endpoint)

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
        # Still fighting with the time....
        logging.info("Changing in: {}  Minutes".format(
            (((int(current_state["nextTime"])/1000)/60)/60)
        ))
        logging.info("Changing at: {}".format(
            self.msec_to_time(
                int(time.time())*1000 +
                int(current_state["nextTime"])
            )
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

        uri = "{}/thermostat/programs".format(self.agreement_id)
        response = self._get(uri)

        self.currenttemp = int(response.json()["currentSetpoint"])/100
        return(self.currenttemp)

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
        logging.info("Getting Energy consumption: %s" % gas_elec)

        uri = "{}/consumption/{}/data".format(
            self.agreement_id, gas_elec
        )
        payload = {
            'fromTime': from_time,
            'toTime': to_time,
            'interval': interval
        }

        response = self._get(uri, payload)  # NOTE shouldnt this be POST?

        logging.debug("last usage from: {} to: {}\n {}".format(
            self.msec_to_time(int(payload["fromTime"])),
            self.msec_to_time(int(payload["toTime"])),
            response
        ))

        return response

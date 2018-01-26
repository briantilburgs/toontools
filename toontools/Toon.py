

import re
import json
import logging

import sys
import uuid
import pprint
import requests
import certifi
import urllib3
import webbrowser

import time

""" The Toon API connection library """


class Toon:
    """ Log in to the Toon API, and do stuff. """
    def __init__(self, authcode, username, password, **kwargs):
        self.apiurl = "https://api.toon.eu"
        self.tokenurl = "https://api.toon.eu/token"
        self.toonapi = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        logging.debug("CertTest is done")
        
        self.username = username
        self.password = password
        logging.debug("Credentials received: %s" % self.username)

        self.clientid = "NIciZ91H4w1AIqEWLLKiTg71URuQEu3s"
        self.clientsecret = "zij4nzKq9oUmVYd7"
        logging.debug("StartingAuth ")
        #self.authenticate_app()
        self.authcode = ""

        self.oauth2key = "Bearer " + self.get_access_token()
        logging.debug("Authorization: %s" % self.oauth2key)
        #self.headers = {'Accept': 'application/json', 'Authorization': self.oauth2key, 'content-type': 'application/json'}
        self.headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': str(self.oauth2key)
          }

        self.agrid = self.get_agreement_id()
        self.statenames = { 0 : "Comfort  ", 1 : "Home     ", 2 : "Sleeping ", 3 : "Away     ", 4 : "Holiday? ", 5 : "VeryCold?"}
        self.max_retries = 3
        self.retry_interval = 1

    def msec_to_time(self, msec):
        date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msec/1000.0))
        return(date_time)

    def get_access_token(self):
        """
        Getting Access code for connecting to Toon API
        """
        logging.info("Authenticate Application to Toon Webform")

        self.authurl = "https://api.toon.eu/authorize/legacy"
        logging.debug("auth url: %s: " % self.authurl)
        headers = {'Accept': 'application/json'}
        formdata = {
            "username": self.username,
            "password" :self.password,
            "response_type": "token",
            "redirect_uri": "http://tilburgs.net",
            "client_id":self.clientid,
            "tenant_id":"eneco",
            "state": "",
            "scope":""
            }
        logging.debug("auth url: %s: " % formdata)

        response  = requests.post(self.authurl, formdata, headers=headers)
        responseurl = response.url
        logging.debug("URL: %s" % response.url)
        logging.debug("StatusCode: %s" % response.status_code)
        logging.debug("Headers: %s" % response.headers)
        if (responseurl.partition("&error=true")[1] == "&error=true"):
            logging.debug("User and Pass invalid, no Token received : %s" % responseurl)
            exit(1)


        self.auth_token = responseurl.partition("#access_token=")[2].partition("&")[0]   
        logging.debug("Access_Token Implicit : %s" % self.auth_token)
        #return(self.auth_token)
        return("aA3TMmpsrmIRfN7BZd5WDbtud2ji")

    def get_agreement_id(self):
        '''
        Module for getting agreement ID

        Expected RESPONSE=
        [
          {
            "agreementId": "",
            "agreementIdChecksum": "",
            "street": "",
            "houseNumber": "",
            "postalCode": "",
            "city": "  ",
            "heatingType": "GAS",
            "displayCommonName": "eneco-000-000000",
            "displayHardwareVersion": "qb2/uni/4.11.6",
            "displaySoftwareVersion": "qb2/uni/4.11.6",
            "isToonSolar": false,
            "isToonly": false
          }
        ]
        '''
        logging.info("Starting Get agreement:")

        uri = "/toon/v3/agreements"
        
        response = requests.get(self.apiurl + uri, headers=self.headers)
        logging.debug("URL: %s" % response.url)
        logging.debug("StatusCode: %s" % response.status_code)
        logging.debug("Headers: %s" % response.headers)
        logging.debug("Response: %s" % response.json())

        try:
            self.agrid = response.json()[0]['agreementId']
            return(self.agrid)

        except:
            logging.info("Error: %s : %s" % (response.json()['fault']['faultstring'], response.json()['fault']['detail']['errorcode']))

    def get_status(self):
        '''
        Getting complete Toon status
        '''
        logging.info("Getting Toon Status:")

        uri = "/toon/v3/" + self.agrid + "/status"
        response = requests.get(self.apiurl + uri, headers=self.headers)
        logging.debug("StatusCode: %s" % response.status_code)
        logging.debug("Response JSON: %s" % (response.json()))

        if response.status_code == 200:   
            self.laststatus = response.json()
        else:
            logging.info("Error: %s" % response.status_code)
            exit(1)

        return(self.laststatus)


    def get_thermostat_states(self):
        '''
        Getting all states with value
        '''
        logging.info("Getting States:")

        uri = "/toon/v3/" + self.agrid + "/thermostat/states"

        response = requests.get(self.apiurl + uri, headers=self.headers)
        logging.debug("StatusCode: %s" % response.status_code)
        logging.debug("Response JSON: %s" % (response.json()))
        
        if response.status_code == 200:
            self.laststates = response.json()
            for state in self.laststates['state']:
                state["name"] = self.statenames[state["id"]]
                logging.info("%s is set to %d C" % (state["name"], state["tempValue"]/100))
        else:
            logging.info("Error: %s" % response.status_code)
            exit(1)

        return(self.laststates)

    def get_thermostat_state_current(self):

        logging.info("Getting Current state:")

        uri = "/toon/v3/" + self.agrid + "/thermostat"

        response = requests.get(self.apiurl + uri, headers=self.headers)
        logging.debug("StatusCode: %s" % response.status_code)
        logging.debug("Response JSON: %s" % (response.json()))

        if response.status_code == 200:
            self.currentstate = response.json()
            logging.info("Current Setpoint:     %dC" % (int(self.currentstate["currentSetpoint"])/100))
            logging.info("Current Temperature:  %dC" % (int(self.currentstate["currentDisplayTemp"])/100))
            logging.info("Current Prog State:   %d " % self.currentstate["programState"])
            logging.info("Current State in Prg: %s " % self.statenames[self.currentstate["activeState"]])
            logging.info("Next State in Prog:   %s " % self.statenames[self.currentstate["nextState"]])
            #Still fighting with the time....
            logging.info("Changing in: %s  Minutes        " % (((int(self.currentstate["nextTime"])/1000)/60)/60))
            logging.info("Changing at: %s          " % (self.msec_to_time(int(time.time())*1000 + int(self.currentstate["nextTime"]))))
            logging.info("Next Temp:            %dC" % (int(self.currentstate["nextSetpoint"])/100))
            logging.info("Real Setpoint:        %dC" % (int(self.currentstate["realSetpoint"])/100))
        else:
            logging.info("Error: %s" % response.status_code)
            exit(1)

        return(self.currentstate)

    def get_thermostat_programs(self):

        logging.info("Getting Thermostat Programs")

        uri = "/toon/v3/" + self.agrid + "/thermostat/programs"
        response = requests.get(self.apiurl + uri, headers=self.headers)
        logging.debug("StatusCode: %s" % response.status_code)
        logging.debug("Response JSON: %s" % (response.json()))

        if response.status_code == 200:
            self.currentprogram = response.json()

        else:
            logging.info("Error: %s" % response.status_code)
            exit(1)

        return(self.currentprogram)

    def get_thermostat_curenttemp(self):

        logging.info("Getting Thermostat Current Temp")

        uri = "/toon/v3/" + self.agrid + "/thermostat/programs"
        response = requests.get(self.apiurl + uri, headers=self.headers)
        logging.debug("StatusCode: %s" % response.status_code)
        logging.debug("Response JSON: %s" % (response.json()))

        if response.status_code == 200:
            self.curenttemp = int(response.json()["currentSetpoint"])/100

        else:
            logging.info("Error: %s" % response.status_code)
            exit(1)
        return(self.curenttemp)

    def get_cons_elec_gas(self, interval='hours', fromtime=1514761200000, totime=(int(time.time())*1000), gas_elec='gas'):
        '''
        Get data from 2018-01-01 00:00:00 till now
        give from and to time in msec
        give gas_elec: "gas|electricity"
        response is like: 
        {   u'hours':   [ {u'timestamp': 1514761200000, u'peak': 0.0, u'unit': u'Wh', u'offPeak': 314.0}, 
                          {u'timestamp': 1514764800000, u'peak': 0.0, u'unit': u'Wh', u'offPeak': 390.0}
                        ], 
            u'weeks': [], 
            u'months': [], 
            u'days': [], 
            u'years': []
        }
        '''
        logging.info("Getting Energy consumption: %s" % gas_elec)

        uri = "/toon/v3/" + self.agrid + "/consumption/" + gas_elec + "/data"
        formdata = {}
        formdata['fromTime'] = fromtime
        formdata['toTime']   = totime
        formdata['interval'] = interval

        #formdata = { 'fromTime': 1514761200000, 'toTime': (int(time.time())*1000), 'interval':'hours'}
        response = requests.get(self.apiurl + uri, formdata, headers=self.headers)
        logging.debug("StatusCode: %s" % response.status_code)
        logging.debug("Response JSON: %s" % (response.json()))
        
        if response.status_code == 200:
            logging.debug("last usage from: %s to: %s \n %s" % (self.msec_to_time(int(formdata["fromTime"])), self.msec_to_time(int(formdata["toTime"])), response.json()))
            requestedconsdata = response.json()
        else:
            logging.info("Error: %s" % response.status_code)
            exit(1)
        return(requestedconsdata)


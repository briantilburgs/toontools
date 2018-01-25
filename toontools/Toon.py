

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
        self.apiurl = "https://api.toon.eu/toon"
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
        self.max_retries = 3
        self.retry_interval = 1

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
        return(self.auth_token)

    def get_agreement_id(self):
        '''
        Module for getting agreement ID
        '''
        logging.debug("Staring Get agreement:")

        """
        https://api.toon.eu/toon/v3/agreements

        curl -X GET --header "Content-Type: application/json" --header "Authorization: Bearer 5Dun0gE0EOlKnQBQwl2niZJsCLhj" "https://api.toon.eu/toon/v3/agreements"
        400
        Bad Request
        500
        Internal server error


        uri = "v3/agreements"

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
        """

        #headers = {
        #            'Accept': '*/*',
        #            'Content-Type': 'application/json',
        #            'Authorization': 'Bearer pPFW2i5Hfw8hkbrgdYdFzM327794'
        #          }
        headers = {
                    'Accept': '*/*',
                    'Content-Type': 'application/json',
                    'Authorization': str(self.oauth2key)
                  }
        #[DEBUG] Headers: {'Content-Type': 'application/json', 'Authorization': u'Bearer 4kFvt020o654ecTbohErivdIsG5z', 'Accept': '*/*'}
        #[DEBUG] Headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer pPFW2i5Hfw8hkbrgdYdFzM327794', 'Accept': '*/*'}
        #[DEBUG] Headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer nqiHpgcouWTC11f10a9yUk8DBTeq', 'Accept': '*/*'}


        logging.debug("Headers: %s" % headers)

        uri = "/v3/agreements"
        
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
        """
        https://api.toon.eu/toon/v3/107088/status
        curl -X GET --header "Content-Type: " --header "Authorization: Bearer 5Dun0gE0EOlKnQBQwl2niZJsCLhj" "https://api.toon.eu/toon/v3/107088/status"
        GET /toon/v3/107088/status HTTP/1.1
        Accept: */*
        Accept-Encoding: br
        Accept-Language:en-us
        Authorization: Bearer 5Dun0gE0EOlKnQBQwl2niZJsCLhj
        Content-Type: application/json
        DNT: 1
        Host: api.toon.eu
        User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML
        X-Forwarded-For: 85.145.22.182
        X-Forwarded-Port: 443
        X-Forwarded-Proto: https
        """

        uri = "/v3/" + self.agrid + "/status"
        response = requests.get(self.apiurl + uri, headers=self.headers)
        
        self.laststatus = response.json()
        logging.debug("URL: %s" % response.url)
        logging.debug("StatusCode: %s" % response.status_code)
        logging.debug("Headers: %s" % response.headers)
        logging.debug("Last status: %s" % (response.json()))
        return(response.json())

    def get_usage_from_to(self):
        '''
        This function should download usage info in hrs/ days/ mnds/ Years
        for a given start till end time in msec
        '''
        #curl -X GET --header "Content-Type: application/json" --header "Authorization: Bearer DXqOMGNXZeFU3XAKf14FoplyGgFa" "https://api.toon.eu/toon/v3/107088/consumption/electricity/data?fromTime=1388530800000&toTime=1420066800000&interval=hours"



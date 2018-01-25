

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
    def __init__(self, authcode, **kwargs):
        self.apiurl = "https://api.toon.eu/toon"
        self.tokenurl = "https://api.toon.eu/token"
        self.toonapi = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        logging.debug("CertTest is done")
        #try:
        #    self.username = kwargs['user']
        #    self.password = kwargs['pasw']
        #    logging.debug("Credentials received: %s" % kwargs['user'])
        #except:
        #    self.username = "toon@username.nl"
        #    self.password = "T00nP@ssword"
        self.clientid = "NIciZ91H4w1AIqEWLLKiTg71URuQEu3s"
        self.clientsecret = "zij4nzKq9oUmVYd7"
        logging.debug("StartingAuth ")
        self.authenticate_app()
        #self.get_access_code()

        self.oauth2key = "Bearer "
        self.headers = {'Accept': 'application/json', 'Authorization': self.oauth2key, 'content-type': 'application/json'}
        #self.agrid = self.get_agreement_id()
        self.max_retries = 3
        self.retry_interval = 1

    def authenticate_app(self):
        """

            <form action="https://api.toon.eu/authorize/legacy" method="post" novalidate>
                <div class="field">
                    <label for="username">Gebruikersnaam</label>
                    <input id="username" type="email" name="username" placeholder="example@toon.nl" />
                </div>
                <div class="field">
                    <label for="password">Wachtwoord</label>
                    <input id="password" name="password" type="password" placeholder="wachtwoord" />
                </div>
                
                <input id="tenant_id" name="tenant_id" type="hidden" value="eneco"/>
                <input id="response_type" name="response_type" type="hidden" value="code"/>
                <input id="client_id" name="client_id" type="hidden" value="NIciZ91H4w1AIqEWLLKiTg71URuQEu3s"/>
                <input id="state" name="state" type="hidden" value=""/>
                <input id="scope" name="scope" type="hidden" value=""/>
        """
        logging.info("Authenticate Application to Tonn Webform")

        self.authurl = "https://api.toon.eu/authorize/legacy"
        logging.debug("auth url: %s: " % self.authurl)

        formdata = {
            "username": "toon@username.nl",
            "password" : "T00nP@ssword",
            "response_type": "code",
            "redirect_uri": "http://google.nl",
            "client_id":self.clientid,
            "tenant_id":"eneco",
            "state": "",
            "scope":""
            }
        logging.debug("auth url: %s: " % formdata)

        response  = requests.post(self.authurl, formdata)
        responseurl = response.url

        logging.debug(responseurl)

        self.auth_code = responseurl.partition("?code=")[2].partition("&")[0]   

        logging.debug("AuthApplication code: %s" % self.auth_code)



    def get_access_code(self):

        #Next Question:
        # curl -k -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "client_id="NIciZ91H4w1AIqEWLLKiTg71URuQEu3s"&client_secret="zij4nzKq9oUmVYd7"&grant_type=authorization_code&code=qxEXGGFb" https://api.toon.eu/token 
        logging.info("Getting Access code for talking to API:")

        self.tokenurl = "https://api.toon.eu/token"
        logging.debug("auth url: %s: " % self.tokenurl)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        #formdata = { 
        #                "client_id": "NIciZ91H4w1AIqEWLLKiTg71URuQEu3s",
        #                "client_secret": "zij4nzKq9oUmVYd7",
        #                "grant_type": "authorization_code",
        #                "code": self.auth_code
        #           }
        formdata = { 
                        "client_id": "NIciZ91H4w1AIqEWLLKiTg71URuQEu3s",
                        "client_secret": "zij4nzKq9oUmVYd7",
                        "grant_type": "authorization_code",
                        "code": "ZntuTXeq"
                   }
        logging.debug("auth url: %s: " % formdata)

        response  = requests.post(self.tokenurl, formdata, headers=headers)

        logging.debug("Resonse Code: %s" % response)
        logging.debug("Resonse Text: %s" % response.text)
        logging.debug("Resonse for GetAccessCode: %s" % response.json)
        self.accessjson = {}
        self.accessjson = response.text
        #logging.debug("AccessCodes: %s, %s, Time valid: %s" % (self.accessjson['access_token'],self.accessjson['refresh_token'],self.accessjson['expires_in']))
        logging.debug(response)
        """
        [DEBUG] Resonse Text: 
            {  
                "access_token": "4AfBK2QMChc0PKG3bCQipPPuUudQ",
                "expires_in": "1799",
                "refresh_token": "AC3LVXIARp0AylX3UKeGjH2xIGx7IUrL",
                "refresh_token_expires_in": "0"
            }

        """

        #Resonse Code: {"fault":{"faultstring":"Invalid Authorization Code","detail":{"errorcode":"keymanagement.service.invalid_request-authorization_code_invalid"}}}

    def refresh_access_code(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        formdata = { 
                        "client_id": "NIciZ91H4w1AIqEWLLKiTg71URuQEu3s",
                        "client_secret": "zij4nzKq9oUmVYd7",
                        "grant_type": "authorization_code",
                        "refresh_token": self.refresh_token
                   }
        """
        curl -k -X POST 
            -H "Content-Type: application/x-www-form-urlencoded"
            -d "client_id=(client_id)
                &client_secret=(client_secret)
                &grant_type=refresh_token
                &refresh_token=(refresh_token)"
            https://api.toon.eu/token
        """
        response  = requests.post(self.tokenurl, formdata, headers=headers)


    def get(self, uri):
        """
        Function for Getting Data from Device and convert to JSON
        """
        logging.debug("posting...", uri)
        response = self.toonapi.request('GET', self.apiurl + uri, headers=self.headers)

        #response = requests.get(self.apiurl + uri, headers=self.headers, verify=True)
        #responsejson = json.loads(response.text)
        status = logging.debug(response.status)
        data = logging.debug(response.read())
        reason = logging.debug(response.reason)
        logging.debug(response.getheader('X-Application-Context'))
        #logging.debug("Status: %d, Reason: %s" % (status, reason))
        logging.debug(data)
        return(response)


    def get_agreement_id(self):
        """
        https://api.toon.eu/toon/v3/agreements

        curl -X GET --header "Content-Type: application/json" --header "Authorization: Bearer 5Dun0gE0EOlKnQBQwl2niZJsCLhj" "https://api.toon.eu/toon/v3/agreements"
        400
        Bad Request
        500
        Internal server error


        uri = "v3/agreements"

        RESPONSE=
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
        uri = "/v3/agreements"
        
        response = self.get(self.apiurl + uri)
        logging.debug("Response: %s" % response)
        #agrid = response[0]['agreementId']
        #self.agreement = response[0]

        return()

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
        response = self.get(uri)
        
        #agrid = response['agreementId']

        self.laststatus = response
        logging.debug("Last status: %s" % (response))

    def set_maxretries(self,max_retries):
            """ Set maximum of retries (default: 3). """
            self.max_retries = max_retries

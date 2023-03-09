import requests
import json
from files.credentials import *

class Request:
    session = requests.Session()
    token = ""

    def __init__(self):
        self.login()

    def login(self):
        try:
            response = self.session.post(host + "/api/v1/login",
            data=json.dumps({"username": username,
                            "password": password}),
            headers={"Content-Type": "application/json"})

            self.token = response.json()['token']
        except:
            self.token = ""
            print("Login failed!")

        
    def get(self,api_params,ctype='application/json'):
        if self.token == "":
            self.login()
            if self.token == "":
                return ""
        details = requests.get(host + api_params,headers = {
            'x-molgenis-token': self.token,
            'Content-Type': ctype
        })
        return details


    def post(self,api_params,ctype='application/json',data={},molg_filename=""):
        if self.token == "":
            self.login()
            if self.token == "":
                return ""
        headers = {
            'x-molgenis-token': self.token,
            'Content-Type': ctype
        }
        if molg_filename != "":
            headers['x-molgenis-filename'] = molg_filename
        details = requests.post(host + api_params, data=data, headers=headers)
        return details


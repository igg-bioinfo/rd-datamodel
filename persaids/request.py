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
            response = self.session.post(host + "v1/login",
                data = json.dumps({"username": username,
                            "password": password}),
                headers = {"Content-Type": "application/json"})
            print("Loged!")

            self.token = response.json()['token']
        except:
            self.token = ""
            print("Login failed!")

        
    def get(self,api_params,ctype='application/json'):
        if self.token == "":
            self.login()
            if self.token == "":
                return ""
        try:
            headers = {
                'x-molgenis-token': self.token,
                'Content-Type': ctype
            }
        
            res = requests.get(host + api_params, headers = headers)
            if res.status_code not in [200,201]:
                #print("GET responded " + str(res.status_code))
                return None
        except:
            print(res.text)
            print("GET for " + api_params + " failed!")
            return None
        return res


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
        try:
            res = requests.post(host + api_params, data = data, headers = headers)
            if res.status_code not in [200,201]:
                print(res.text)
                #print("POST responded " + str(res.status_code))
                return None
        except:
            print("POST for " + api_params + " failed!")
            return None
        return res


    def put(self,api_params,ctype='application/json',data={},molg_filename=""):
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
        try:
            res = requests.put(host + api_params, data = data, headers = headers)
            if res.status_code not in [200,201]:
                print(res.text)
                #print("POST responded " + str(res.status_code))
                return None
        except:
            print("POST for " + api_params + " failed!")
            return None
        return res

import requests
import json
import logging
from requests.exceptions import ConnectTimeout


#A class responsible for making api call via request library
class APIManager:
    def __init__(self, url, access_token=None):
        self.url = url
        self.access_token = access_token
    

    # Make the GET request using the requests library
    def _get(self):
        # Construct the Header
        headers={"Content-Type": "application/json"}
        #check if access_token is required
        if self.access_token != None:
            # Add access token to header
            headers.update({"Authorization": "Bearer {}".format(self.access_token)})
        try:
            response = requests.get(self.url, headers=headers, timeout=20)
            #Log response from slack
            logging.info(f"Response status code: {response.status_code} - Response body: {response.text}")
        except ConnectTimeout:
            return "ConnectTimeout"
        return response



    # Make the POST request using the requests library
    def _post(self, body_params=None):
        # Construct the Header
        headers={"Content-Type": "application/x-www-form-urlencoded"}
        #check if access_token is required
        if self.access_token != None:
            # Add access token to header
            headers.update({"Authorization": "Bearer {}".format(self.access_token)})
        try:
            if body_params == None:
                response = requests.post(self.url, headers=headers, timeout=20)
            else:
                response = requests.post(self.url, data=body_params, headers=headers, timeout=20)
            #Log response from slack
            logging.info(f"Response status code: {response.status_code} - Response body: {response.text}")
        except ConnectTimeout:
            return "ConnectTimeout"
        return response
    



from dotenv import load_dotenv
import os
import requests as req
import time
from typing import Dict, List, Optional

load_dotenv()

BASE_URL = "https://api-gateway.instructure.com"
CLIENT_ID = os.getenv("API_KEY")
CLIENT_SECRET = os.getenv("API_SECRET")

class CanvasAPI:

    def __init__(self, client_id: str, client_secret: str, auto_login: bool = True) -> None: 
        self.url = BASE_URL
        self.client_id = client_id
        self. client_secret = client_secret
        if auto_login: 
            self.login()

    
    def login(self) -> Optional[str]: 
        url = f"{self.url}/ids/auth/login"
        auth = req.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        data = {"grant_type": "client_credentials"}
        response = req.post(url, auth=auth, data=data)

        if response.status_code == 200:
            response_json = response.json()
            self.access_token = response_json.get("access_token")  # Store the token
            return self.access_token
        else:
            raise Exception(f"Login failed with status code: {response.status_code}, response text: {response.text}")
        
    
    def make_request_with_auth(self, method: str, endpoint: str, **kwargs) -> req.Response:
        """Makes a request to the Canvas API with authentication."""
        if self.access_token is None:
            raise Exception("Not logged in. Please call login() first.")

        url = f"{self.url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = req.request(method, url, headers=headers, **kwargs)
        return response
    
    def get_list_of_tables(self) -> Optional[List]:
        if self.access_token is None:
            raise Exception("Not logged in. Please call login() first.")
        response = self.make_request_with_auth("GET", "/dap/query/canvas/table")
        if response.status_code == 200:
            return response.json()["tables"]
        else:
            return [{"status code": response.status_code, "msg": response.text}]
        
    def get_schema_of_table(self, table_name: str) -> Optional[Dict]:
        response = self.make_request_with_auth("GET", f"dap/query/canvas/table/{table_name}/schema")
        if response.status_code == 200:
            return response.json()
        else:
            return {"status code": response.status_code, "msg": response.text}
    
    def get_id_for_table(self, table_name: str) -> Optional[str]:
        body = {"format": "csv"}
        response = self.make_request_with_auth("POST", f"dap/query/canvas/table/{table_name}/data", json=body)

        if response.status_code == 200:
            response_json = response.json()
            request_id = response_json.get("id")

            while True:
                time.sleep(1)
                response = self.make_request_with_auth("GET", f"dap/query/canvas/table/{table_name}/data/{request_id}")
                status = response.json().get("status")
                print(status)
            
                if status != "complete":
                    continue
                
                print(response_json)  # Or process the data as needed
                break
        else:
            return f"Initial request failed with status code: {response.status_code},response text: {response.text}"
    
    def get_table_by_name(self, table_name:str):
        endpoint = "dap/object/url"

        # table_request_id = self.get_id_for_table(table_name)
        body = [
            {
                "id": ""
            }
        ]

        headers = {
            "x-instauth": self.access_token,
            "Content-Type": "application/json", 
        }

        # Set the request payload
        payload = {
            "headers": headers,
            "json": body,
        }

        response = req.post(f"{self.url}/{endpoint}", **payload)
        print(response.json())
        print(response.json()["urls"].values())


        if response.status_code == 200:
            print("Request successful. Response:")
            print(response.json())
        else:
            print("Request failed with status code:", response.status_code)
            print("Response text:", response.text)
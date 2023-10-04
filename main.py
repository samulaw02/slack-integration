from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException, status, Request
from typing_extensions import Annotated
from fastapi.responses import JSONResponse
import config
import requests
from models import *
import os
import hashlib
import hmac
import json

app = FastAPI()


@lru_cache()
def get_settings():
    return config.Settings()


# Define a boolean variable to indicate the success of the OAuth connection
oauth_connection_successful = False


# Build the OAuth 2.0 redirect URL with required parameters (client_id, scope, redirect_uri, etc.)
@app.get("/authorize")
def slack_oauth_redirect(settings: Annotated[config.Settings, Depends(get_settings)]):
    try:
        oauth_params = {
            "client_id": settings.CLIENT_ID,
            "scope": settings.SCOPE
        }
        # Construct the OAuth 2.0 authorization URL
        oauth_url = f"{settings.OAUTH_AUTHORIZE_URL}?" + "&".join(f"{key}={value}" for key, value in oauth_params.items())

        # Return a JSON response with the OAuth URL
        return JSONResponse(content={"status" : True, "url": oauth_url}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"status": False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)




# Exchange the authorization code for an access token by making a POST request to Slack
@app.get("/post_authorize", response_model=CallPostAuthorizeRes)
def slack_oauth_callback(code: str, settings: Annotated[config.Settings, Depends(get_settings)]):
    try:
        # call the global connection variable
        global oauth_connection_successful
        # Parameters for making the POST request to exchange the code for an access token
        token_request_data = {
            "client_id": settings.CLIENT_ID,
            "client_secret": settings.CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.REDIRECT_URL,
            "grant_type": "authorization_code",
        }

        # Make the POST request using the requests library
        response = requests.post(settings.TOKEN_EXCHANGE_URL, data=token_request_data)
        # Log the response to the console
        print(response.text)
        if response.status_code == 200:
            response_json = response.json()
            # Check if slack response was successful
            if "ok" in response_json and response_json["ok"] == True:
                # Create a CallPostAuthorizeRes instance with the required data
                result = CallPostAuthorizeRes(
                    status = True,
                    protected_data={
                        "access_token" : response_json["access_token"],
                        "bot_user_id" : response_json["bot_user_id"]
                    },
                    consent_user=response_json["authed_user"]["id"],
                    metadata={
                        "scope" : response_json["scope"],
                        "app_id" : response_json["app_id"]
                    }
                )
                # Set oauth_connection_successful to True if successful
                oauth_connection_successful = True
                return result
            else:
                error = response_json["error"] if "error" in response_json else ""
                return JSONResponse(content={"status" : False, "detail" : "OAuth post authorization failed. Reason: {}".format(error)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JSONResponse(content={"status" : False, "detail" : "OAuth post authorization failed. Please try again"}, status_code=response.status_code)
    except requests.exceptions.RequestException as e:
        return JSONResponse(content={"status" : False, "details" : "OAuth post authorization request failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JSONResponse(content={"status" : False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)




#list all the users in the integration.
@app.post("/get_users_page", response_model=GetUsersPageRes)
def get_users_page(request: GetUsersPageReq, settings: Annotated[config.Settings, Depends(get_settings)]):
    try:
        # Construct the Header
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(request.page_token)
        }
        # Construct the URL
        url = settings.SLACK_API_BASE_URL + "/users.list"
        # Make the POST request to slack api to get list of users
        response = requests.post(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            response_json = response.json()
            # Check if slack response was successful
            if "ok" in response_json and response_json["ok"] == True:
                result = GetUsersPageRes(page_token=request.page_token, users=response_json["members"])
                return result
            else:
                error = response_json["error"] if "error" in response_json else ""
                return JSONResponse(content={"status" : False, "detail" : "OAuth post authorization failed. Reason: {}".format(error)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JSONResponse(content={"status" : False, "details" : "Get list of users failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.exceptions.RequestException as e:
        return JSONResponse(content={"status" : False, "details" : "Get list of users request failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JSONResponse(content={"status" : False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



#list all apps connected to A user..
@app.post("/get_apps_per_user", response_model=GetAppsRes)
def get_apps_per_user(request: GetAppsReq, settings: Annotated[config.Settings, Depends(get_settings)]):
    try:
        # Construct the Header
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(request.page_token)
        }
        # Construct the URL
        url = settings.SLACK_API_BASE_URL + "/admin.apps.requests.list"
        # Make the POST request to slack api to get list of apps connected to a user
        response = requests.post(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            response_json = response.json()
            # Check if slack response was successful
            if "ok" in response_json and response_json["ok"] == True:
                result = GetAppsRes(page_token=request.page_token, apps=response_json["app_requests"])
                return result
            else:
                error = response_json["error"] if "error" in response_json else ""
                return JSONResponse(content={"status" : False, "detail" : "Get list of apps authorization failed. Reason: {}".format(error)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JSONResponse(content={"status" : False, "details" : "Get list of apps failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.exceptions.RequestException as e:
        return JSONResponse(content={"status" : False, "details" : "Get list of apps failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JSONResponse(content={"status" : False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



#list all apps connected to A user..
@app.post("/run", response_model=GetRunRes)
def get_apps_per_user(request: GetRunReq, settings: Annotated[config.Settings, Depends(get_settings)]):
    try:
        final_output = {}
        # Construct the Header
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(request.page_token)
        }
        # Construct the URL for list of users
        url = settings.SLACK_API_BASE_URL + "/users.list"
        # Make the POST request to slack api to get list of users
        response = requests.post(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            response_json = response.json()
            # Check if slack response was successful
            if "ok" in response_json and response_json["ok"] == True:
                users=response_json["members"]
                apps = []
                # Construct the URL for list of apps to a specific user
                url = settings.SLACK_API_BASE_URL + "/admin.apps.requests.list"
                # Make the POST request to slack api to get list of apps
                response = requests.post(url, headers=headers)
                print(response.text)
                if response.status_code == 200:
                    response_json = response.json()
                    if "ok" in response_json and response_json["ok"] == True:
                        apps=response_json["app_requests"]
                final_output = {
                    "users" : users,
                    "apps" : apps
                }
                result = GetRunRes(page_token=request.page_token, data=final_output)
                return result
            else:
                error = response_json["error"] if "error" in response_json else ""
                return JSONResponse(content={"status" : False, "detail" : "Get list of comprehensive data failed. Reason: {}".format(error)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JSONResponse(content={"status" : False, "details" : "Get list of comprehensive data failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.exceptions.RequestException as e:
        return JSONResponse(content={"status" : False, "details" : "Get list of comprehensive data failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JSONResponse(content={"status" : False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    




#Verify if there is a valid token from oauth redirect..
@app.get("/verify", response_model=GetVerificationRes)
def get_apps_per_user():
    try:
        global oauth_connection_successful
        result = GetVerificationRes(connection_status=oauth_connection_successful)
        return result
    except requests.exceptions.RequestException as e:
        return JSONResponse(content={"status" : False, "details" : "Get verification status failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JSONResponse(content={"status" : False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

#Slack Event wehook
@app.post("/events")
async def slack_event(request: Request, settings: Annotated[config.Settings, Depends(get_settings)]):
    try:
        # Verify the request came from Slack
        signature = request.headers.get("X-Slack-Signature")
        timestamp = request.headers.get("X-Slack-Request-Timestamp")
        request_body = await request.body()
        slack_signing_secret = settings.SIGNING_SECRET
        is_valid_request = verify_request(request_body, signature, timestamp, slack_signing_secret)
        if not is_valid_request:
            raise HTTPException(status_code=401, detail="Invalid request")
        event_data = json.loads(request_body.decode("utf-8"))
        event_type = event_data.get("type")
        if event_type == "event_callback":
            event = event_data.get("event")
            '''A file_share message is sent when a file is shared into a channel, group or direct message.
            Check if the event type is a message and file is involve '''
            if event.get("type") == "message" and "files" in event:
                # Extract file information
                files = event.get("files")
                for file in files:
                    user = event.get("user")
                    file_size = file.get("size")
                    file_type = file.get("filetype")
                    timestamp = file.get("timestamp")
                    
                    # Download and save the file
                    file_url = file.get("url_private")
                    print(event)
                    try:
                        file_path = download_and_save_file(file_url)
                    except Exception as e:
                        print(str(e))
                    # Print file information
                    print(f"User: {user}")
                    print(f"File Size: {file_size} bytes")
                    print(f"File Type: {file_type}")
                    print(f"Timestamp: {timestamp}")
                    print(f"File Path: {file_path}")
        if event_type == "url_verification":
            return event_data.get("challenge")
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(content={"status": False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


def verify_request(request_body, signature, timestamp, slack_signing_secret):
    print("body{}-signature{}-timestamp{}-slack_signing_secret{}".format(request_body,signature,timestamp,slack_signing_secret))
    # Verify that the request came from Slack
    request_signature = "v0=" + hmac.new(
        bytes(slack_signing_secret, "utf-8"),
        msg=bytes(f"v0:{timestamp}:{request_body.decode('utf-8')}", "utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(request_signature, signature)



def download_and_save_file(file_url):
    try:
        # Download the file
        response = requests.get(file_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to download file")

        # Define the root directory of your project
        project_root = os.path.dirname(os.path.abspath(__file__))

        # Define the path to the media folder (create it if it doesn't exist)
        media_folder = os.path.join(project_root, "media")
        os.makedirs(media_folder, exist_ok=True)

        # Define the file path within the media folder
        file_path = os.path.join(media_folder, os.path.basename(file_url))

        # Check if the response content type is an image
        content_type = response.headers.get('content-type')
        print(content_type)
        if content_type and content_type.startswith('image'):
            # Save the file to the specified path
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
        else:
            raise HTTPException(status_code=400, detail="Not an image file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing_extensions import Annotated
from fastapi.responses import JSONResponse
import config
from models import *
from helpers import *
from middleware import RequestResponseLoggingMiddleware
from api_manager import APIManager
import json

app = FastAPI()

# Create an instance of HTTPBearer
bearer = HTTPBearer()


# Add the custom middleware to the app
# app.add_middleware(RequestResponseLoggingMiddleware)

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
            "scope": settings.SCOPE,
            "user_scope": settings.USER_SCOPE
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
        print(code)
        #Api manager initialization
        api_manager = APIManager(url=settings.TOKEN_EXCHANGE_URL)
        response = api_manager._post(token_request_data)
        if response == "ConnectTimeout":
            return JSONResponse(content={"status" : False, "detail" : "Service unavailable: Connection timeout while making an API call."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif response.status_code == 200:
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
    except Exception as e:
        return JSONResponse(content={"status" : False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)




#list all the users in the integration.
@app.post("/get_users_page", response_model=GetUsersPageRes)
def get_users_page(settings: Annotated[config.Settings, Depends(get_settings)], credentials: HTTPAuthorizationCredentials = Depends(bearer), request: GetUsersPageReq = None):
    try:
        # Extract the token from credentials
        access_token = credentials.credentials
        # Construct the URL
        url = settings.SLACK_API_BASE_URL + "/users.list"
        #Api manager initialization
        api_manager = APIManager(url=url, access_token=access_token)
        #check if page_token is sent from the request, this logic is used to set the cursor
        if request == None:
            body_params = None
        else:
            body_params = {"cursor" : request.page_token}
        # Make the POST request to slack api to get list of users
        response = api_manager._post(body_params)
        if response == "ConnectTimeout":
            return JSONResponse(content={"status" : False, "detail" : "Service unavailable: Connection timeout while making an API call."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif response.status_code == 200:
            response_json = response.json()
            # Check if slack response was successful
            if "ok" in response_json and response_json["ok"] == True:
                #result = GetUsersPageRes(page_token=response_json["response_metadata"]["next_cursor"], users=response_json["members"])
                result = parse_get_users_page(response_json)
                return result
            else:
                error = response_json["error"] if "error" in response_json else ""
                return JSONResponse(content={"status" : False, "detail" : "OAuth post authorization failed. Reason: {}".format(error)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JSONResponse(content={"status" : False, "details" : "Get list of users failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JSONResponse(content={"status" : False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



#list all apps connected to A user..
@app.post("/get_apps_per_user", response_model=GetAppsRes)
def get_apps_per_user(request: GetAppsReq, settings: Annotated[config.Settings, Depends(get_settings)], credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        # Extract the token from credentials
        access_token = credentials.credentials
        # Construct the URL
        url = settings.SLACK_API_BASE_URL + "/admin.apps.requests.list"
        #Api manager initialization
        api_manager = APIManager(url=url, access_token=access_token)
        # Make the POST request to slack api to get list of apps connected to a user
        response = api_manager._post()
        if response == "ConnectTimeout":
            return JSONResponse(content={"status" : False, "detail" : "Service unavailable: Connection timeout while making an API call."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif response.status_code == 200:
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
        #Api manager initialization
        api_manager = APIManager(url=url, access_token=request.page_token)
        # Make the POST request to slack api to get list of users
        response = api_manager._post()
        if response == "ConnectTimeout":
            return JSONResponse(content={"status" : False, "detail" : "Service unavailable: Connection timeout while making an API call."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == 200:
            response_json = response.json()
            # Check if slack response was successful
            if "ok" in response_json and response_json["ok"] == True:
                users=response_json["members"]
                apps = []
                # Construct the URL for list of apps to a specific user
                list_of_app_url = settings.SLACK_API_BASE_URL + "/admin.apps.requests.list"
                #re-assign url to api manager
                api_manager.url = list_of_app_url
                # Make the POST request to slack api to get list of apps
                response = api_manager._post()
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
    except Exception as e:
        return JSONResponse(content={"status" : False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    




#Verify if there is a valid token from oauth redirect..
@app.get("/verify", response_model=GetVerificationRes)
def get_apps_per_user():
    try:
        global oauth_connection_successful
        result = GetVerificationRes(connection_status=oauth_connection_successful)
        return result
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
            '''
            A file_share message is sent when a file is shared into a channel,
            group or direct message. Check if the event type is a message and file is involve 
            '''
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
                    try:
                        file_path = download_and_save_file(file_url)
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error encounter while downloading and saving file due to {e}")
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
        raise HTTPException(status_code=500, detail=f"Internal server error due to {e}")
    



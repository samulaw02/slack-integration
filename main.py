from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException, status
from typing_extensions import Annotated
from fastapi.responses import JSONResponse
import config
import requests
from models import *

app = FastAPI()


@lru_cache()
def get_settings():
    return config.Settings()


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
        return JSONResponse(content={"status" : False, "details" : "OAuth request failed. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JSONResponse(content={"status" : False, "detail" : "Internal Server Error. Reason: {}".format(str(e))}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
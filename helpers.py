from fastapi import HTTPException
import requests
import os
import hashlib
import hmac
from models import *



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
            # Save the file to the specified path
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
            raise HTTPException(status_code=400, detail="Not an image file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


# Mapping the JSON response to the GetUsersPageRes model
def parse_get_users_page(slack_response_json):
    user_records = []
    # Iterate over "members" starting from the second element (first element is always the slackbot)
    for member in slack_response_json["members"][1:]:
        user = UserRecord(
            org_id=member["team_id"],
            int_name=member["name"],
            user_id=member["id"],
            primary_email=None if not "email" in member["profile"] else member["profile"]["email"],
            is_admin=member["is_admin"],
            suspended=member["deleted"],
            name = UserName(
                givenName = member["profile"]["display_name"],
                familyName = member["profile"]["last_name"],
                fullName = member["profile"]["first_name"] + member["profile"]["last_name"]
            ),
            extra_data = member["profile"]
        )
        user_records.append(user)
    result = GetUsersPageRes(page_token=slack_response_json["response_metadata"]["next_cursor"], users=user_records)
    return result

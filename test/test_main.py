import os
from fastapi.testclient import TestClient
from main import app
from models import *  # Import your response model
from dotenv import load_dotenv


load_dotenv()
client = TestClient(app)





# Define a test Settings class with appropriate properties for your tests
class TestSettings:
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URL = os.getenv("REDIRECT_URL")
    TOKEN_EXCHANGE_URL = os.getenv("TOKEN_EXCHANGE_URL")
    OAUTH_AUTHORIZE_URL = os.getenv("OAUTH_AUTHORIZE_URL")
    SCOPE = os.getenv("SCOPE")



def test_authorize_endpoint():
    response = client.get("/authorize")
    assert response.status_code == 200
    assert response.json() == {"status": True, "url": "https://slack.com/oauth/v2/authorize?client_id=4705501911553.5967586783863&scope=users:read,users.profile:read,usergroups:read"}



def test_post_authorize_endpoint():
    # Replace 'YOUR_AUTHORIZATION_CODE' with an actual authorization code
    authorization_code = 'YOUR_AUTHORIZATION_CODE'

    response = client.get(f"/post_authorize?code={authorization_code}")
    assert response.status_code == 200
    # Assuming you have specific response validation, perform it here
    # assert response.json() == {"status": True, ...}

    


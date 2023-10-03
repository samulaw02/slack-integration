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


# Test the "/authorize" endpoint
def test_authorize_endpoint():
    settings = TestSettings()
    response = client.get("/authorize")
    assert response.status_code == 200
    oauth_params = {
        "client_id": settings.CLIENT_ID,
        "scope": settings.SCOPE
    }
    # Construct the OAuth 2.0 authorization URL
    oauth_url = f"{settings.OAUTH_AUTHORIZE_URL}?" + "&".join(f"{key}={value}" for key, value in oauth_params.items())
    assert response.json() == {"status": True, "url": oauth_url}


# Test the "/post_authorize" endpoint
def test_post_authorize_endpoint():
    # Replace 'YOUR_AUTHORIZATION_CODE' with an actual authorization code
    authorization_code = 'YOUR_AUTHORIZATION_CODE'
    response = client.get(f"/post_authorize?code={authorization_code}")
    assert response.status_code == 200
    assert response.json() == {"status": True}



# Test the "/get_users_page" endpoint
def test_get_users_page():
    # Replace with valid request data as needed
    request_data = {
        "page_token": "your_page_token"
    }
    response = client.post("/get_users_page", json=request_data)
    assert response.status_code == 200
    # Modify this assertion based on your expected response
    assert "users" in response.json() and "page_token" in response.json()


# Test the "/get_apps_per_user" endpoint
def test_get_apps_per_user():
    # Replace with valid request data as needed
    request_data = {
        "page_token": "your_page_token"
    }
    response = client.post("/get_apps_per_user", json=request_data)
    assert response.status_code == 200
    # Modify this assertion based on your expected response
    assert "apps" in response.json() and "page_token" in response.json()

# Test the "/run" endpoint
def test_get_run():
    # Replace with valid request data as needed
    request_data = {
        "page_token": "your_page_token"
    }
    response = client.post("/run", json=request_data)
    assert response.status_code == 200
    # Modify this assertion based on your expected response
    assert "users" in response.json() and "apps" in response.json() and "page_token" in response.json()

# Test the "/verify" endpoint
def test_verify_connection():
    response = client.get("/verify")
    assert response.status_code == 200
    assert "connection_status" in response.json()

    


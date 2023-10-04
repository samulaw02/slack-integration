# Project Documentation

## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)
- [Endpoints](#endpoints)
  - [/authorize](#authorize)
  - [/post_authorize](#post_authorize)
  - [/get_users_page](#get_users_page)
  - [/get_apps_per_user](#get_apps_per_user)
  - [/run](#run)
  - [/verify](#verify)
- [Models](#models)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This documentation provides an overview of the FastAPI project, its endpoints, models, and how to set it up, test, and deploy.

## Setup

### Prerequisites

Before setting up the project, ensure you have the following prerequisites installed:

- Python 3.8+
- `pip` (Python package manager)
- [Docker](https://www.docker.com/) (for containerization, optional)

### Installation

1. Clone the repository:
    <pre>
    ```
    git clone <repository_url>
    cd <repository_directory>
    ```
   </pre>


2. Create a virtual environment (optional but recommended):
   <pre>
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
    </pre>

3. Install the required dependencies:
    <pre>
    ```
    pip install -r requirements.txt
    ```
    </pre>


4. Set Up Environment Variables:
   Create a .env file with the following content, replacing placeholders with your actual values:
   <pre>
   ```
   APP_ID=your_app_id
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   SIGNING_SECRET=your_signing_secret`
   OAUTH_AUTHORIZE_URL=your_oauth_authorize_url
   REDIRECT_URL=your_redirect_url
   TOKEN_EXCHANGE_URL=your_token_exchange_url
   SLACK_API_BASE_URL=your_slack_api_base_url
   SCOPE="your_scope"
   ```
   </pre>


5. Run the FastAPI Application:
   `uvicorn main:app --host 0.0.0.0 --port 8000`

6. Access the FastAPI Interactive Documentation:
   Open a web browser and go to http://localhost:8000/docs to test the endpoints interactively.



## Endpoint

-   /authorize
    -   [Description]: Generates an OAuth 2.0 authorization URL for Slack integration.
    -   [HTTP Method]: GET
    -   [Parameters]: None
    -   [Response]: JSON with the authorization URL.
    
    Example Request:
    `GET /authorize`

    Example Response:
    <pre>
    ```
    {
    "status": true,
    "url": "https://slack.com/oauth2/authorize?client_id=your_client_id&scope=your_scope"
    }
    ```
    </pre>

-   /post_authorize
    -   [Description]: Exchanges an authorization code for an access token.
    -   [HTTP Method]: GET
    -   [Parameters]: code (authorization code)
    -   [Response]: JSON with the access token and user information.
    
    Example Request:
    `GET /post_authorize?code=your_authorization_code`
    
    Example Response:
    </pre>
    ```
    {
    "status": true,
    "protected_data": {
        "access_token": "your_access_token",
        "bot_user_id": "your_bot_user_id"
    },
    "consent_user": "authed_user_id",
    "metadata": {
        "scope": "your_scope",
        "app_id": "your_app_id"
    }
    }
    ```
    </pre>

    Continue documenting the other endpoints in a similar manner.

##  Models
This section describes the Pydantic models used in the project. Please refer to the code for the complete model definitions. The models include:

[Settings]: Represents configuration settings.
[CallPostAuthorizeRes]: Represents the response model for the /post_authorize endpoint.
Other models for request and response data.

##  Testing
To run the project's unit tests, use the following command:

`pytest test/test_main.py`

To run the functional tests, use the following command:
`pytest test/test_main.py -k <name_of_function>`



##  Deployment
For deployment, you can containerize the application using Docker. Create a Dockerfile and use a production-ready web server like Gunicorn to serve the application.

##  Contributing
If you'd like to contribute to this project, please follow the standard GitHub fork and pull request workflow.

##  License
This project is licensed under the [LICENSE NAME] license. See the LICENSE.md file for details.



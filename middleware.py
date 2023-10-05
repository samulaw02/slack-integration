from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import logging
import json  # Import the json module for parsing JSON

# Configure logging
logging.basicConfig(level=logging.INFO)

# Custom middleware for logging requests and responses
class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request, call_next: RequestResponseEndpoint
    ):
        # Log the incoming request
        logging.info(f"Incoming Request: {request.method} {request.url}")
        logging.info(f"Headers: {request.headers}")

        # Check if the request has a body
        if hasattr(request, 'body'):
            request_body = await request.body()
            if request_body:
                try:
                    # Parse the JSON request body
                    json_data = json.loads(request_body.decode('utf-8'))
                    logging.info(f"JSON Body: {json_data}")
                except json.JSONDecodeError:
                    logging.info("Body: (Not JSON)")

        # Call the next middleware or route handler
        response = await call_next(request)

        # Log the outgoing response
        logging.info(f"Outgoing Response: {response.status_code}")
        logging.info(f"Headers: {response.headers}")

        # Check if the response has a body
        if hasattr(response, 'body'):
            response_body = await response.body()
            if response_body:
                # Assuming the response is also JSON
                try:
                    json_data = json.loads(response_body.decode('utf-8'))
                    logging.info(f"JSON Response Body: {json_data}")
                except json.JSONDecodeError:
                    logging.info("Response Body: (Not JSON)")

        return response
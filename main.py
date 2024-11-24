import logging
from fastapi import FastAPI, HTTPException, Header, Request, status
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler, Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
from script import Run
import os

# Set up FastAPI application
app = FastAPI()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.state.limiter = limiter


# Direct API keys (hardcoded)
API_KEYS = {
    "user1": "1a2b3C4d5E6f7G8h9I0J1K2L3M4N5O6",
    "user2": "7z8Y9A0B1C2D3E4F5G6H7I8J9K0L1M2",
    "user3": "9X1Y2Z3A4B5C6D7E8F9G0H1I2J3K4L5",
    "user4": "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5",
    "user5": "F1g2H3i4J5K6l7M8n9O0p1q2r3S4T5",
    "user6": "U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5",
    "user7": "P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5",
    "user8": "M1N2O3P4Q5R6S7T8U9V0W1X2Y3Z4A5",
    "user9": "B1C2D3E4F5G6H7I8J9K0L1M2N3O4P5",
    "user10": "Q1R2S3T4U5V6W7X8Y9Z0A1B2C3D4E5"
}

# Set up logging configuration (log only to a file)
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO for production
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log")  # Log only to a file
    ]
)

# Define Pydantic model for user input
class UserInput(BaseModel):
    system_prompt: str
    message: str
    tokens: int

# Endpoint for serving model response
@app.post("/response")
@limiter.limit("100 per day, 20 per minute")
async def app_response(request: Request, user_data: UserInput, x_api_key: str = Header(None)):
    try:
        # Validate the API key
        if x_api_key not in API_KEYS.values():
            logging.warning(f"Invalid API key attempted: {x_api_key}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key! Authorization revoked.")
        
        # Validate input data types
        if not isinstance(user_data.system_prompt, str) or not isinstance(user_data.message, str) or not isinstance(user_data.tokens, int):
            logging.error(f"Invalid input types. system_prompt: {type(user_data.system_prompt)}, message: {type(user_data.message)}, tokens: {type(user_data.tokens)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input format.")

        # Handle the model run
        output = Run(user_data.system_prompt, user_data.message, user_data.tokens)
        logging.info(f"Model response generated successfully for {request.client.host}")
        return output
    except HTTPException as e:
        logging.error(f"HTTP exception occurred: {str(e)}")
        raise e  # Re-raise the exception to send back to the user
    except Exception as e:
        logging.exception("Unexpected error occurred.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

# Global Variables
used_keys = []  # Track used API keys
user_address = []  # Track users who have generated keys
user_generated_time = {}  # Track users for generated time

@app.get("/generate_api")
async def generate_api_key(request: Request):
    user_ip = get_remote_address(request)
    global used_keys
    global user_address
    global user_generated_time

    try:
        # Check if the user has already generated an API key
        if user_ip in user_address:
            user_time = user_generated_time.get(user_ip, "Unknown Time")
            logging.warning(f"API key already generated for IP: {user_ip} at {user_time}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"API key already generated at {user_time} from IP: {user_ip}")
        
        # Generate a new API key for the user
        for key, value in API_KEYS.items():
            if value not in used_keys:
                user_address.append(user_ip)
                used_keys.append(value)  # Store the used key
                generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_generated_time[user_ip] = generation_time  # Store the generation time for the user
                logging.info(f"API key generated for IP: {user_ip} at {generation_time}")
                return {
                    "One Time API key": value,
                    "Generation Time": generation_time,
                    "!": "Don't share this secret API key."
                }

        # If no keys are available, return an error
        logging.error("No available API keys to generate.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No API keys available!")
    
    except HTTPException as e:
        logging.error(f"HTTP exception occurred: {str(e)}")
        raise e  # Re-raise the exception to send back to the user
    except Exception as e:
        logging.exception("Unexpected error occurred during API key generation.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

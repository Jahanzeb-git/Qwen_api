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


# Access API keys
API_KEYS = {
    "user1": os.getenv("API_KEY_USER1"),
    "user2": os.getenv("API_KEY_USER2"),
    "user3": os.getenv("API_KEY_USER3"),
    "user4": os.getenv("API_KEY_USER4"),
    "user5": os.getenv("API_KEY_USER5"),
    "user6": os.getenv("API_KEY_USER6"),
    "user7": os.getenv("API_KEY_USER7"),
    "user8": os.getenv("API_KEY_USER8"),
    "user9": os.getenv("API_KEY_USER9"),
    "user10": os.getenv("API_KEY_USER10"),
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

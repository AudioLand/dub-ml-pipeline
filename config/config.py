import json
import os

import openai
from dotenv import load_dotenv

load_dotenv()

# Environment
IS_DEV_ENVIRONMENT = os.getenv("ENVIRONMENT") == "development"

# APIs
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
LABS11_API_KEY = os.getenv("11LABS_API_KEY")
GENDER_DETECTION_API_URL = os.getenv("GENDER_DETECTION_API_URL")
GENDER_DETECTION_BEARER_TOKEN = os.getenv("GENDER_DETECTION_BEARER_TOKEN")
ENDPOINT_WHISPER_API_URL = os.getenv("ENDPOINT_WHISPER_API_URL")

# Firebase
CERTIFICATE_CONTENT = json.loads(os.getenv("FIREBASE_CERTIFICATE_CONTENT"))
BUCKET_NAME = os.getenv("BUCKET_NAME")
UPDATE_PROJECT_URL = os.getenv("UPDATE_PROJECT_URL")
UPDATE_USER_TOKENS_URL = os.getenv("UPDATE_USER_TOKENS_URL")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")

# Set OpenAI API key
openai.api_key = OPEN_AI_API_KEY

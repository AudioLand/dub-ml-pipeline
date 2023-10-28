import json
import os

from dotenv import load_dotenv

load_dotenv()

# Environment
IS_DEV_ENVIRONMENT = os.getenv("ENVIRONMENT") == "development"

# APIs
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
LABS11_API_KEY = os.getenv("11LABS_API_KEY")
GENDER_DETECTION_API_URL = os.getenv("GENDER_DETECTION_API_URL")
GENDER_DETECTION_BEARER_TOKEN = os.getenv("GENDER_DETECTION_BEARER_TOKEN")

# Firebase
CERTIFICATE_CONTENT = json.loads(os.getenv("FIREBASE_CERTIFICATE_CONTENT"))
BUCKET_NAME = os.getenv("BUCKET_NAME")
UPDATE_PROJECT_URL = os.getenv("UPDATE_PROJECT_URL")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")

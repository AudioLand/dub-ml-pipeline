import firebase_admin
from firebase_admin import credentials

from config.config import CERTIFICATE_PATH


def init_firebase():
    cred = credentials.Certificate(CERTIFICATE_PATH)
    firebase_admin.initialize_app(cred)

# db = firestore.client()

# PROJECT_COLLECTION = "projects"
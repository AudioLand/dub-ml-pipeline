import firebase_admin
from firebase_admin import credentials, firestore

CERTIFICATE_PATH = "integrations/firebase/audioland-dub-firebase-adminsdk-xfwtj-4228d1d618.json"


def init_firebase():
    cred = credentials.Certificate(CERTIFICATE_PATH)
    firebase_admin.initialize_app(cred)

# db = firestore.client()

# PROJECT_COLLECTION = "projects"

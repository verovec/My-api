import os
import uuid
import time
import datetime
import jwt

import sys
sys.path.append("..")

from utils.hash import sha256

FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

class JWToken:

    id = False
    user_id = False
    expires_at = False

    initialized = False

    def __init__(self, task: str, parameter: str):
        if task == "init":
            self.initialize(parameter)
        elif task == "decode":
            self.decode(parameter)

    def initialize(self, user_id):
        """
        Initializes a JSON Web Token with a random ID
        and expiration date of now + 3 hours for a specific user.
        """
        self.id = sha256(str(uuid.uuid4) + str(self.expires_at))
        self.expires_at = time.time() + 10800.0 # 3 hours
        self.user_id = user_id
        self.initialized = True

    def encode(self):
        return jwt.encode({
            "id": self.id,
            "user_id": self.user_id,
            "expires_at": self.expires_at
        }, FLASK_SECRET_KEY, algorithm='HS256').decode("utf-8")

    def decode(self, encoded_payload: str):
        try:
            decoded_payload = jwt.decode(encoded_payload, FLASK_SECRET_KEY, algorithms=['HS256'])
            if ("expires_at" in decoded_payload and "id" in decoded_payload and "user_id" in decoded_payload):
                self.id = decoded_payload["id"]
                self.user_id = decoded_payload["user_id"]
                self.expires_at = float(decoded_payload["expires_at"])
                if (self.expires_at - time.time() > 0):
                    self.initialized = True
            else:
                self.initialized = False
        except Exception as e:
            print(e)
            self.initialized = False
    
    def __repr__(self):
        return "<JWToken(id='{}', expires_at='{}', initialized='{}')>".format(
            self.id,
            self.expires_at,
            self.initialized
        )
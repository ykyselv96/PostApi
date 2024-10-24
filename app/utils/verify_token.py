import jwt
from core.config import system_config

class VerifyToken():
    """Does all the token verification using PyJWT"""

    def __init__(self, token):
        self.token = token
        self.config = system_config.settings
        self.secret_key = self.config.jwt_access_secret_key

    def verify(self):
        try:
            payload = jwt.decode(
                self.token,
                self.secret_key,
                algorithms=self.config.algorithm
            )
        except jwt.ExpiredSignatureError:
            return {"status": "error", "message": "Token has expired."}
        except jwt.InvalidTokenError as error:
            return {"status": "error", "message": "Token is invalid."}

        return payload

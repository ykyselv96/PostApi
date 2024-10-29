from typing import Any
import jwt
from core.config import system_config


class VerifyToken():
    """Does all the token verification using PyJWT"""

    def __init__(self, token):
        self.token = token
        self.config = system_config.settings
        self.secret_key = self.config.jwt_access_secret_key

    def verify(self) -> dict[str, Any]:
        """
        Verifies the JWT token and decodes its payload.

        Returns:
            dict: A dictionary containing the payload if valid, or an error message if invalid.
        """
        try:
            payload = jwt.decode(
                self.token,
                self.secret_key,
                algorithms=self.config.algorithm
            )
        except jwt.ExpiredSignatureError:
            return {"status": "error", "message": "Token has expired."}
        except jwt.InvalidTokenError:
            return {"status": "error", "message": "Token is invalid."}

        return payload

# app/authutils.py
from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import requests
import json
import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

class AzureADAuthenticator:
    def __init__(self, tenant_id: str, client_id: str):
        self.tenant_id = tenant_id
        self.client_id = "api://2d830ac7-1a1e-4a51-a5f9-04fb25ba4c19"
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.jwks_url = f"{self.authority}/discovery/v2.0/keys"
        self.jwks = self._load_jwks()
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def _load_jwks(self):
        try:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            return response.json()["keys"]
        except Exception as e:
            raise Exception(f"Failed to load JWKS: {str(e)}")

    def _build_rsa_key(self, jwk):
        n = int.from_bytes(base64.urlsafe_b64decode(self._pad_base64(jwk["n"])), "big")
        e = int.from_bytes(base64.urlsafe_b64decode(self._pad_base64(jwk["e"])), "big")
        public_key = rsa.RSAPublicNumbers(e, n).public_key(backend=default_backend())
        return public_key

    def _pad_base64(self, b64_string):
        return b64_string + "=" * (-len(b64_string) % 4)

    def verify_token(self, token: str):
        try:
            unverified_header = jwt.get_unverified_header(token)
            key = next((k for k in self.jwks if k["kid"] == unverified_header["kid"]), None)

            if not key:
                raise HTTPException(status_code=401, detail="Public key not found")

            public_key = self._build_rsa_key(key)

            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience="api://2d830ac7-1a1e-4a51-a5f9-04fb25ba4c19"
            )

            return payload
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    def get_current_user(self):
        async def current_user(token: str = Depends(self.oauth2_scheme)):
            return self.verify_token(token)
        return current_user

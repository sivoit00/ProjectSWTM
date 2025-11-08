# backend/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import requests

# OAuth2 Bearer Token lesen
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Keycloak-Konfiguration
KEYCLOAK_REALM_URL = "http://localhost:8080/realms/fahrzeugservice"
ALGORITHM = "RS256"

def get_public_key():
    # JWKS vom Keycloak Realm abrufen
    r = requests.get(f"{KEYCLOAK_REALM_URL}/protocol/openid-connect/certs")
    jwks = r.json()
    key = jwks["keys"][0]
    public_key = f"-----BEGIN PUBLIC KEY-----\n{key['x5c'][0]}\n-----END PUBLIC KEY-----"
    return public_key

PUBLIC_KEY = get_public_key()

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM], audience="account")
        return payload  # payload enthält Userinfos wie username, email, roles
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

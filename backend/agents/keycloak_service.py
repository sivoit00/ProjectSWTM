"""
Keycloak authentication and token validation service.
"""
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import os

security = HTTPBearer()


KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "fahrzeugservice")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "frontend")


def get_keycloak_public_key() -> str:
    """
    Fetch the public key from Keycloak to verify JWT tokens.
    """
    try:
        url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        realm_info = response.json()
        public_key = realm_info.get("public_key")
        
        if not public_key:
            raise ValueError("Public key not found in realm info")
        
        
        return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
    
    except Exception as e:
        print(f"Error fetching Keycloak public key: {e}")
        return None


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a Keycloak JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        public_key = get_keycloak_public_key()
        if not public_key:
            return None
        
        # Decode the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=KEYCLOAK_CLIENT_ID,
            options={"verify_aud": False}  # Keycloak doesn't always include audience
        )
        
        return payload
    
    except JWTError as e:
        print(f"JWT decode error: {e}")
        return None
    except Exception as e:
        print(f"Token validation error: {e}")
        return None


def get_user_email_from_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Optional[str]:
    """
    Extract user email from Keycloak token.
    
    Args:
        credentials: HTTP Bearer credentials from FastAPI
        
    Returns:
        User email address or None
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        return None
    
    
    email = payload.get("email")
    
    return email


def require_auth(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Require authentication for an endpoint.
    Raises HTTPException if token is invalid.
    
    Args:
        credentials: HTTP Bearer credentials from FastAPI
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload


def get_optional_user_email(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> Optional[str]:
    """
    Try to extract user email from token, but don't fail if token is missing/invalid.
    This is useful for endpoints that work both with and without authentication.
    
    Args:
        credentials: HTTP Bearer credentials from FastAPI
        
    Returns:
        User email address or None
    """
    try:
        if not credentials:
            return None
        
        return get_user_email_from_token(credentials)
    except:
        return None

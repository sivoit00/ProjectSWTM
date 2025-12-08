import os
import logging
from jose import jwt, JWTError
from typing import Optional
import requests

log = logging.getLogger(__name__)

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "fahrzeugservice")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "frontend")


def get_keycloak_public_key() -> str:
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
        log.error(f"Failed to fetch Keycloak public key: {e}")
        raise


def verify_token(token: str) -> dict:
    try:
        public_key = get_keycloak_public_key()
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=KEYCLOAK_CLIENT_ID,
            options={"verify_aud": False}
        )
        
        return payload
    except JWTError as e:
        log.warning(f"Token verification failed: {e}")
        raise ValueError("Invalid token")
    except Exception as e:
        log.error(f"Token verification error: {e}")
        raise


def extract_user_info(payload: dict) -> dict:
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "name": payload.get("name") or payload.get("preferred_username"),
        "roles": payload.get("realm_access", {}).get("roles", []),
        "client_roles": payload.get("resource_access", {}).get(KEYCLOAK_CLIENT_ID, {}).get("roles", [])
    }

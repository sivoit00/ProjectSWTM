# Authentication Implementation

## Übersicht

Sichere API-Endpoints mit Keycloak JWT-Token-Validierung.

## Struktur

```
backend/auth/
├── __init__.py           # Exports
├── keycloak_auth.py      # Token-Verifikation
└── dependencies.py       # FastAPI Dependencies
```

## Verwendung

### Geschützte Endpoints

```python
from auth.dependencies import get_current_user

@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"user": current_user["name"]}
```

### Admin-Endpoints

```python
from auth.dependencies import require_role

@router.get("/admin")
def admin_route(current_user: dict = Depends(require_role("admin"))):
    return {"message": "Admin access"}
```

### Optionale Authentifizierung

```python
from auth.dependencies import get_optional_user

@router.post("/public")
async def public_route(user: Optional[dict] = Depends(get_optional_user)):
    if user:
        return {"message": f"Hello {user['name']}"}
    return {"message": "Hello Guest"}
```

## User Context

```python
{
    "user_id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "roles": ["user", "admin"],
    "client_roles": ["frontend-user"]
}
```

## Geschützte Routes

- `/kunden/*` - Kundenverwaltung
- `/auftraege/*` - Auftragsverwaltung
- `/fahrzeuge/*` - Fahrzeugverwaltung
- `/files/upload` - File Upload
- `/admin/guardrails/*` - Admin-Only (benötigt "admin" Rolle)

## Öffentliche Routes

- `/ki-orchestrator/message` - Chat (optional auth)
- `/docs` - API Dokumentation

## Testing

### Mit gültigem Token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/kunden
```

### Ohne Token (401):

```bash
curl http://localhost:8000/kunden
```

## Environment Variables

```env
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=fahrzeugservice
KEYCLOAK_CLIENT_ID=frontend
```

## Error Responses

- `401 Unauthorized` - Kein oder ungültiger Token
- `403 Forbidden` - Token gültig, aber fehlende Rolle
- `500 Internal Server Error` - Auth-Service Fehler

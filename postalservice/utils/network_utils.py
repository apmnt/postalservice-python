import base64
import uuid
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import httpx
from jose import jwt

def get_pop_jwt(url, method="GET"):
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    header = {
        "typ": "dpop+jwt",
        "alg": "ES256",
        "jwk": {
            "crv": "P-256",
            "kty": "EC",
            "x": base64.urlsafe_b64encode(public_key.public_numbers().x.to_bytes(32, 'big')).rstrip(b'=').decode('utf-8'),
            "y": base64.urlsafe_b64encode(public_key.public_numbers().y.to_bytes(32, 'big')).rstrip(b'=').decode('utf-8'),
        },
    }

    payload = {
        "iat": int(time.time()),
        "jti": str(uuid.uuid4()), 
        "htu": url,
        "htm": method,
        "uuid": str(uuid.uuid4()),
    }

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    pop_jwt = jwt.encode(payload, private_key_pem,
                         algorithm='ES256', headers=header)
    
    return pop_jwt

async def fetch_async(url):
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url)
        return response

#!/usr/bin/env python3
"""
Flask Session Decoder
Decodes Flask session cookies (without signature verification).
"""

import sys
import zlib
from flask.sessions import session_json_serializer
from itsdangerous import base64_decode

def decode_flask_session(cookie: str):
    """
    Decodes a Flask session cookie.
    Flask sessions are '.' separated: [payload].[timestamp].[signature]
    """
    try:
        # Split the cookie parts
        parts = cookie.split('.')
        if len(parts) < 3:
            return "Invalid session format. Expected at least 2 dots."

        payload_b64 = parts[0]
        
        # Handle decompression if payload starts with '.'
        decompress = False
        if payload_b64.startswith('!'): # Flask uses '!' for compressed sessions in some versions
             payload_b64 = payload_b64[1:]
             decompress = True
        elif payload_b64.startswith('.'):
            payload_b64 = payload_b64[1:]
            decompress = True

        # Base64 decode
        payload_bytes = base64_decode(payload_b64)

        # Zlib decompress if needed
        if decompress:
            payload_bytes = zlib.decompress(payload_bytes)

        # Deserialize JSON
        return session_json_serializer.loads(payload_bytes)

    except Exception as e:
        return f"Error decoding session: {str(e)}"

def main():
    if len(sys.argv) > 1:
        cookie = sys.argv[1]
    else:
        # Default example from the original script
        cookie = "eyJjdXJyZW50X3dpZmkiOiJhMTE5ZGRlYTIzYWZkOWViMDcxYjZkNTljZmU1YzAxZC5qcGciLCJpc2FkbWluIjpmYWxzZX0.ZdRscQ.RpWsyg2iM58p5yidDF70FMLxOjc"
        print(f"[*] No cookie provided. Decoding default example...")

    decoded = decode_flask_session(cookie)
    
    import json
    print("\nDecoded Session Content:")
    print(json.dumps(decoded, indent=4))

if __name__ == "__main__":
    main()

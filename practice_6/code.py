import jwt

with open("key.pem", "rb") as f:
    private_key = f.read()
    
payload = {"login": "testuser", "is_admin": True}
token = jwt.encode(payload, private_key, algorithm="RS256")
print(token)
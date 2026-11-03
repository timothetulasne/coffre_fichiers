import base64
import hmac
import hashlib

token_intercepte = "YWxpY2V8MTc5MzM3MDQzMA==.2680ce47bd21780a5a16741c3485e925dcc060b125dddcf6654f39fe4c0600fb"

liste = ["secret","password","admin","default","mines","test","polytech","azerty","école","polytech2027"]

def brute_force(token,L):
    try:
        encoded_payload, signature_recue = token.split(".")
        payload = base64.urlsafe_b64decode(encoded_payload)
    except ValueError:
        return
    
    for mot in L:
        signature_calculee = hmac.new(mot.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        
        if signature_calculee == signature_recue:
            return mot
    return None

print(brute_force(token_intercepte,liste))
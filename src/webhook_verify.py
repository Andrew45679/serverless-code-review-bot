"""
This file contains the function to verify webhook signatures.
It takes the payload, signature, and secret as input and returns True if the signature is valid, False otherwise.
"""
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    # Make sure that the signature and secret are not None or empty
    if not signature or not secret:
        return False
    
    # Make sure that the signature starts with "sha256="
    if "sha256=" not in signature:
        return False

    # Calculate the expected signature using HMAC with SHA256
    expected_signature = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

    # Return the result of the signature comparison
    return hmac.compare_digest(expected_signature, signature[7:])



    

    
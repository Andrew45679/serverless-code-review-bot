"""
Unit tests for verify_signature() in src/webhook_verify.py.

Run with:
    python -m pytest tests/test_webhook_verify.py
"""

import hashlib
import hmac
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from webhook_verify import verify_signature

SECRET = "test-secret-123"
PAYLOAD = '{"action":"opened","number":42}'

# Compute one real, correctly-formed signature to reuse across the cases.
digest = hmac.new(SECRET.encode("utf-8"), PAYLOAD.encode("utf-8"), hashlib.sha256).hexdigest()
VALID_SIGNATURE = f"sha256={digest}"


def test_valid_signature_returns_true():
    assert verify_signature(PAYLOAD, VALID_SIGNATURE, SECRET) is True


def test_wrong_secret_returns_false():
    assert verify_signature(PAYLOAD, VALID_SIGNATURE, "wrong-secret") is False


def test_missing_signature_returns_false():
    assert verify_signature(PAYLOAD, "", SECRET) is False
    assert verify_signature(PAYLOAD, None, SECRET) is False


def test_missing_secret_returns_false():
    assert verify_signature(PAYLOAD, VALID_SIGNATURE, "") is False
    assert verify_signature(PAYLOAD, VALID_SIGNATURE, None) is False


def test_malformed_signature_prefix_returns_false():
    assert verify_signature(PAYLOAD, "not-a-real-signature", SECRET) is False


def test_sha1_prefix_returns_false():
    sha1_digest = hmac.new(SECRET.encode("utf-8"), PAYLOAD.encode("utf-8"), hashlib.sha1).hexdigest()
    sha1_signature = f"sha1={sha1_digest}"
    assert verify_signature(PAYLOAD, sha1_signature, SECRET) is False
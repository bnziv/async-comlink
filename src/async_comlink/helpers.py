import hashlib
import hmac
import time
import logging
from json import dumps

def get_logger():
    """
    Get a debug logger
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('{name}\t{levelname} - {message}', style='{')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

def get_hmac(endpoint, secret_key, access_key, payload):
    """
    Helper function to get HMAC headers
    """
    current_time = str(int(time.time() * 1000))
    headers = {"X-Date": current_time}

    signature = hmac.new(key=secret_key.encode(), digestmod=hashlib.sha256)
    signature.update(current_time.encode())
    signature.update('POST'.encode())
    signature.update(endpoint.encode())

    if payload:
        payload = dumps(payload, separators=(',', ':')).encode()
    else:
        payload = dumps({}).encode()
        
    payload_digest = hashlib.md5(payload).hexdigest()
    signature.update(payload_digest.encode())
    signature_digest = signature.hexdigest()

    headers['Authorization'] = f'HMAC-SHA256 Credential={access_key},Signature={signature_digest}'
    return headers
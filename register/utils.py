import random
import string
from django.conf import settings
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder


# Will generate a random alphanumeric string with 62^length possible combinations
def generate_random_key(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_signature_key():
    """
    Generate a new random signing key and return the hex-encoded bytestring
    """
    signing_key = SigningKey.generate()
    return signing_key.encode(encoder=HexEncoder).decode("utf-8")


def load_signature_key():
    """
    Load the signature key from the environment
    """
    key = settings.QRCODE_SIGNATURE_PRIVATE_KEY
    key_bytes = key.encode("utf-8")
    try:
        signing_key = SigningKey(key_bytes, encoder=HexEncoder)
    except TypeError:
        print("Missing or faulty QRCode signing key")
        raise
    return signing_key


def get_poster_payload():
    pass


def sign_payload():
    pass

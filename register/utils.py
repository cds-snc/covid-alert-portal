import random
import string
from django.conf import settings
from nacl.signing import SigningKey
from nacl.encoding import Base64Encoder
import pyqrcode
import io


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
        signing_key = SigningKey(key_bytes, encoder=Base64Encoder)
    except TypeError:
        print("Missing or faulty QRCode signing key")
        raise
    return signing_key


def get_poster_payload():
    pass


def sign_payload():
    pass

def generate_qr_code(location):

    # Create payload
    payload = "{short_code}\n{name}\n{address}, {city}".format(
        short_code=location.short_code,
        name=location.name,
        address=location.address,
        city=location.city,
    )
    print(payload)

    # Encode payload
    payload_bytes = payload.encode()
    print("Payload bytes:")
    print(payload_bytes)

    # Sign payload
    signing_key = load_signature_key()
    signed_b64 = signing_key.sign(payload_bytes, encoder=Base64Encoder)
    print("Signed base64")
    print(signed_b64)

    # Build URL
    url_prefix = "https://retrieval.wild-samphire.cdssandbox.xyz/exposure-configuration/download.html#"
    url = url_prefix + str(signed_b64.decode())
    print(url)

    qrcode = pyqrcode.create(url)

    buffer = io.BytesIO()
    qrcode.svg(buffer, xmldecl=False, scale=3)
    
    return buffer.getvalue().decode()
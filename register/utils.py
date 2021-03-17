import random
import string
from django.conf import settings
from nacl.signing import SigningKey
from nacl.encoding import Base64Encoder
import segno
import io


# Will generate a random alphanumeric string with 62^length possible combinations
def generate_random_key(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_signature_key():
    """
    Generate a new random signing key and return the hex-encoded bytestring
    """
    signing_key = SigningKey.generate()
    return signing_key.encode(encoder=Base64Encoder).decode("utf-8")


def load_signature_key():
    """
    Load the signature key from the environment
    """
    try:
        key = settings.QRCODE_SIGNATURE_PRIVATE_KEY
        key_bytes = key.encode("utf-8")
    except AttributeError:
        print("Missing QRCode signing key")
        raise

    try:
        signing_key = SigningKey(key_bytes, encoder=Base64Encoder)
    except TypeError:
        print("Faulty QRCode signing key")
        raise
    return signing_key


def generate_payload(location):
    payload = "{short_code}\n{name}\n{address}, {city}".format(
        short_code=location.short_code,
        name=location.name,
        address=location.address,
        city=location.city,
    )
    return payload


def sign_payload(payload):
    payload_bytes = payload.encode()
    signing_key = load_signature_key()
    signed_b64 = signing_key.sign(payload_bytes, encoder=Base64Encoder)
    return signed_b64.decode()


def generate_qrcode(url):
    qrcode = segno.make_qr(url)

    buffer = io.BytesIO()
    qrcode.save(buffer, kind="svg", xmldecl=False, scale=5, omitsize=True)

    return buffer.getvalue().decode()


def get_signed_qrcode(location):
    # Create payload
    payload = generate_payload(location)

    # Sign payload
    signed = sign_payload(payload)

    # Build URL
    url_prefix = "https://alpha.canada.ca/covid-alert.html#"
    url = url_prefix + str(signed)

    qrcode = generate_qrcode(url)
    return qrcode

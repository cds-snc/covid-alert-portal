import random
import string
from django.conf import settings
from nacl.signing import SigningKey
from nacl.encoding import Base64Encoder
import segno
import io
import cairosvg
from django.template.loader import render_to_string
import base64
import PyPDF2
import os


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


def get_pdf_poster(location, lang="en"):
    # Generate the qr code
    qr_code = get_signed_qrcode(location)
    poster_template = "register/posters/{lang}.svg".format(lang=lang)

    address_details = "{city}, {province} {postal_code}".format(
        city=location.city,
        province=location.province,
        postal_code=location.postal_code,
    )

    # Render the qr code and address details into the svg template
    rendered = render_to_string(
        poster_template,
        {
            "qr_code": qr_code,
            "name": location.name,
            "address": location.address,
            "address_details": address_details,
        },
    )

    buffer = io.BytesIO()

    # Convert the rendered SVG to PDF
    cairosvg.svg2pdf(
        bytestring=rendered.encode("UTF-8"),
        write_to=buffer,
        output_width=815,
    )

    # Get instructions PDF
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    instructions = os.path.join(
        BASE_DIR,
        "register/templates/register/posters/instructions-{lang}.pdf".format(lang=lang),
    )
    pdf_instructions = PyPDF2.PdfFileReader(instructions)

    # Merge the pdfs
    mergeFile = PyPDF2.PdfFileMerger()
    mergeFile.append(pdf_instructions)
    mergeFile.append(buffer)

    # Write it back to the puffer
    mergeFile.write(buffer)
    buffer.seek(0)

    return buffer


def get_encoded_poster(location, lang="en"):
    poster = get_pdf_poster(location, lang)
    poster_str = poster.read()

    # Base64-encode the poster for attaching
    poster_encoded = base64.b64encode(poster_str).decode()
    return poster_encoded

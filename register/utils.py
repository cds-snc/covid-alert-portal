import base64
import qrcode
import json

# TODO: we probably need to store this or serialize it or something
def generate_qr_code(location):
    payload = get_payload(location)
    img = qrcode.make(payload)


# Returns a serialized/base64 encoded JSON object containing the
# Location code and name, prefixed by the app prefix
def get_payload(location):
    prefix = "covidalert://QRCode/"
    payload = json.dumps({"code": str(location.id), "name": location.name})
    payload_b64 = base64.b64encode(payload.encode()).decode()
    return prefix + payload_b64

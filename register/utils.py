import random
import string


# Will generate a random alphanumeric string with 62^length possible combinations
def generate_random_key(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

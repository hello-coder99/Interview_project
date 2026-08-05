import random
import string

host_url="http://localhost/"

def generate_new_url(length=6):
    characters=string.ascii_letters+string.digits
    url=''.join(random.choice(characters) for _ in range(length))
    return host_url+url


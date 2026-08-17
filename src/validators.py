import re
from .config import CUSTOM_DOMAIN

def validate_bucket_name(bucket_name):
    pattern = r"^[a-z0-9-]{3,63}$"
    return bool(re.match(pattern,bucket_name))


def is_custom_domain_enabled():
    return bool(CUSTOM_DOMAIN)
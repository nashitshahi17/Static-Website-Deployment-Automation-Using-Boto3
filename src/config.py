import uuid

AWS_REGION = "ap-south-1"
BUCKET_NAME = "static-site"

def create_bucket_name():
    suffix = str(uuid.uuid4())[:8]
    return f"{BUCKET_NAME}-{suffix}"


import uuid

AWS_REGION = "ap-south-1"
BUCKET_NAME = "static-site"

def create_bucket_name():
    suffix = str(uuid.uuid4())[:8]
    return f"{BUCKET_NAME}-{suffix}"

def get_website_endpoint(bucket_name):
    return (
        f"http://{bucket_name}.s3-website."
        f"{AWS_REGION}.amazonaws.com"
    )


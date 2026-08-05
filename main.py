from src.config import (create_bucket_name, get_website_endpoint )
from src.s3_manager import S3Manager
from src.uploader import WebsiteUploader
# import boto3
# def main():
#     s3 = boto3.client('s3')

#     response = s3.list_buckets()

#     print("Buckets in your account: \n")

#     for bucket in response.get("Bucket",[]):
#         print(f"-{bucket['Name']}")

def main():
    BUCKET_NAME = create_bucket_name()
    manager = S3Manager()
    manager.create_bucket(BUCKET_NAME)
    manager.configure_public_access(BUCKET_NAME)
    manager.apply_public_bucket_policy(BUCKET_NAME)
    manager.enable_static_website(BUCKET_NAME)
    uploader = WebsiteUploader(manager.s3)
    uploader.upload_directory(BUCKET_NAME,"website")

    print("Website Endpoint\n")
    print(get_website_endpoint(BUCKET_NAME))

if __name__ == "__main__":
    main()
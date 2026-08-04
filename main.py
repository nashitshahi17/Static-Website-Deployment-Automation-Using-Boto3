from src.config import BUCKET_NAME
from src.s3_manager import S3Manager
# import boto3
# def main():
#     s3 = boto3.client('s3')

#     response = s3.list_buckets()

#     print("Buckets in your account: \n")

#     for bucket in response.get("Bucket",[]):
#         print(f"-{bucket['Name']}")

def main():
    manager = S3Manager()
    manager.create_bucket(BUCKET_NAME)

if __name__ == "__main__":
    main()
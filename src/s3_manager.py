import boto3
from botocore.exceptions import ClientError

from .config import AWS_REGION

class S3Manager:
    def __init__(self):
        self.s3 = boto3.client('s3',region_name = AWS_REGION)

    def create_bucket(self,bucket_name):
        try:
            if AWS_REGION == 'us-east-1':
                response = self.s3.create_bucket(Bucket= bucket_name)
            else:
                response = self.s3.create_bucket(
                    Bucket = bucket_name,
                    CreateBucketConfiguration={
                        "LocationConstraint": AWS_REGION
                    }
                )
            print(f"Bucket '{bucket_name} created sucessfully'")
        except ClientError as e:
            print(f"Failed to create bucket: {e}")
            raise
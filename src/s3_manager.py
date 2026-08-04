import boto3
from botocore.exceptions import ClientError
from .logger import logger
from .validators import validate_bucket_name

from .config import AWS_REGION

class S3Manager:
    def __init__(self):
        self.s3 = boto3.client('s3',region_name = AWS_REGION)

    def create_bucket(self,bucket_name):
        try:
            if not validate_bucket_name(bucket_name):
                raise ValueError("Invalid bucket name")
            if AWS_REGION == 'us-east-1':
                response = self.s3.create_bucket(Bucket= bucket_name)
            else:
                response = self.s3.create_bucket(
                    Bucket = bucket_name,
                    CreateBucketConfiguration={
                        "LocationConstraint": AWS_REGION
                    }
                )
            logger.info(f"Bucket '{bucket_name}' created sucessfully")
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "BucketAlreadyExists":
                logger.warning("Bucket name already taken globally")
            elif error_code == "BucketAlreadyOwnedByYou":
                logger.warning("Bucket already exists in your account")
            else:
                logger.error(f'AWS error: {e}')
            raise
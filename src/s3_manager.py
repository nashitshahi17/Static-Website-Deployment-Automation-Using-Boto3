import boto3
import json
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

    def configure_public_access(self,bucket_name):
        '''Disable Block Public Access setting so Bucket can
        host a public static webiste'''

        try:
            self.s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration = {
                    "BlockPublicAcls":False,
                    "IgnorePublicAcls":False,
                    "BlockPublicPolicy":False,
                    "RestrictPublicBuckets":False
                }
            )
            logger.info("Public Access Block disabled")

        except ClientError as e:
            logger.error(e)
            raise

    def enable_static_website(self,bucket_name):
        try:
            self.s3.put_bucket_website(
                Bucket = bucket_name,
                WebsiteConfiguration={
                    "IndexDocument":{
                        "Suffix":"index.html"
                    },
                    "ErrorDocument":{
                        "Key":"error.html"
                    }
                }
            )
            logger.info("Static Website Hosting Enabled")
        except ClientError as e:
            logger.error(e)
            raise

    def apply_public_bucket_policy(self,bucket_name):
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        try:
            self.s3.put_bucket_policy(
                Bucket = bucket_name,
                Policy = json.dumps(policy)
            )
            logger.info("Public bucket policy applied successfully")
        except ClientError as e:
            logger.error(e)
            raise
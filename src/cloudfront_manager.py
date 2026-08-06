import boto3
import uuid
from botocore.exceptions import ClientError
from .logger import logger

class CloudFrontManager:

    def __init__(self):
        self.client = boto3.client('cloudfront')

    def create_oac(self):
        try:
            response = self.client.create_origin_access_control(
                OriginAccessControlConfig={
                    "Name": f"static-site-oac-{uuid.uuid4().hex[:8]}",
                    "Description": "Origin Access Control for Static Website",
                    "SigningProtocol": "sigv4",
                    "SigningBehavior": "always",
                    "OriginAccessControlOriginType": "s3"
                }
            )

            oac = response["OriginAccessControl"]

            logger.info("Origin Access Control created successfully.")

            return {
                "Id": oac["Id"],
                "ETag": response["ETag"]
            }

        except ClientError as e:
            logger.error(f"Failed to create OAC: {e}")
            raise
    
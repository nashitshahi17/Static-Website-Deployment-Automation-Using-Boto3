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

    def create_distribution(self,website_endpoint):
        try:
            origin_id = "S3WebsiteOrigin"

            distribution_config = {
                "CallerReference": str(uuid.uuid4()),
                "Comment": "Static Website CloudFront Distribution",
                "Enabled": True,
                "DefaultRootObject":"index.html",
                "Origins":{
                    "Quantity":1,
                    "Items":[
                        {
                            "Id": origin_id,
                            "DomainName":website_endpoint,
                            "CustomOriginConfig":{
                                "HTTPPort":80,
                                "HTTPSPort":443,
                                "OriginProtocolPolicy":"http-only"
                            }
                        }
                    ]
                },
                "DefaultCacheBehavior":{
                    "TargetOriginId": origin_id,
                    "ViewerProtocolPolicy":"redirect-to-https",
                    "AllowedMethods":{
                        "Quantity": 2,
                        "Items": [
                            "GET",
                            "HEAD"
                        ],
                        "CachedMethods": {
                            "Quantity": 2,
                            "Items": [
                                "GET",
                                "HEAD"
                            ]
                        }
                    },

                    "Compress": True,

                    "ForwardedValues": {
                        "QueryString": False,
                        "Cookies": {
                            "Forward": "none"
                        }
                    }
                }
            }
            response = self.client.create_distribution(
            DistributionConfig=distribution_config
            )

            distribution = response["Distribution"]

            logger.info(
                f"CloudFront distribution created: "
                f"{distribution['Id']}"
            )

            return {
                "Id": distribution["Id"],
                "DomainName": distribution["DomainName"],
                "Status": distribution["Status"]
            }
        except ClientError as e:
            logger.error(
                f"Failed to create CloudFront distribution: {e}"
            )
            raise


    def wait_for_deployment(self, distribution_id):
        try:
            logger.info(
                f"Waiting for CloudFront distribution "
                f"{distribution_id} to deploy..."
            )

            waiter = self.client.get_waiter(
                "distribution_deployed"
            )

            waiter.wait(
                Id=distribution_id
            )

            logger.info(
                "CloudFront distribution is now deployed."
            )

            return self.get_distribution(distribution_id)

        except ClientError as e:
            logger.error(
                f"Error while waiting for CloudFront deployment: {e}"
            )
            raise

    def get_distribution(self,distribution_id):
        try:
            response = self.client.get_distribution(Id=distribution_id)
            distribution = response["Distribution"]
            return {
                "Id": distribution["Id"],
                "ARN": distribution["ARN"],
                "Status": distribution["Status"],
                "DomainName": distribution["DomainName"]
            }
        except ClientError as e:
            logger.error(f"Failed to retrieve CloudFront distribution: {e}")
            raise

    def create_invalidation(self,distribution_id,paths):
        try:
            if not paths:
                logger.info("No paths provided for invalidation")
                return None

            invalidation_paths = [
                path if paths.startswith("/") else f"/{path}"
                for path in paths
            ]

            response = self.client.create_invalidation(
                DistributionId = distribution_id,
                InvalidationBatch = {
                    "Paths":{
                        "Quantity" : len(invalidation_paths),
                        "Items": invalidation_paths
                    },
                    "CallerReference": str(uuid.uuid4())
                }
            )

            invalidation = response["Invalidation"]

            logger.info(
                f"CloudFront Invalidation created: "
                f"{invalidation['Id']}"
            )
            return{
                "Id":invalidation["Id"],
                "Status": invalidation["Status"]
            }
        except ClientError as e:
            logger.info(
                f"Failed to create CloudFront invalidation: {e}"
            )
            raise

    def wait_for_invalidation(self,distribution_id,invalidation_id):
        try:
            logger.info(
                f"Waiting for invalidation "
                f"{invalidation_id} to complete..."
            )

            waiter = self.client.get_waiter(
                "invalidation_completed"
            )

            waiter.wait(
                DistributionId=distribution_id,
                Id=invalidation_id
            )

            logger.info(
                "CloudFront invalidation completed."
            )

        except ClientError as e:
            logger.error(
                f"Failed while waiting for invalidation: {e}"
            )
            raise

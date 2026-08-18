import boto3
from botocore.exceptions import ClientError
from .logger import logger

class CleanupManager:
    def __init(self):
        self.s3 = boto3.client("s3")

        self.cloudfront = boto3.client("cloudfront")

        self.acm = boto3.client("acm",region_name = "us-east-1")

        self.route53 = boto3.client("route53")

    def get_resources_from_state(self,state):
        resources = {
            "bucket_name": state.get("bucket_name"),
            "distribution_id": state.get("distribution_id"),
            "cloudfront_domain": state.get("cloudfront_domain"),
            "Certificate_arn": state.get("certificate_arn"),
            "hosted_zone_id": state.get("hosted_zone_id"),
            "oac_id": state.get("oac_id")
        }
        return resources

    def preview_cleanup(self,resources):
        logger.info("=========Clenaup Dry Run===========")
        for resource, identifier in resources.items():
            if identifier:
                logger.info(f"{resource}: {identifier}")
            else:
                logger.info(f"{resource}: None")
        logger.info("No AWS Resources were deleted")
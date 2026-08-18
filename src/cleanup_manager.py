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

    def delete_bucket_object(self,bucket_name):
        logger.info(f"Deleting objects from bucket: {bucket_name}")

        paginator = self.s3.get_paginator("list_objects_v2")

        deleted_count = 0

        for page in paginator.paginate(Bucket = bucket_name):
            objects = page.get("Contents",[])
            if not objects:
                continue
            object_identifiers = [
                {
                    "Key": obj["Key"]
                }
                for obj in objects
            ]

            self.s3.delete_object(Bucket = bucket_name,Delete = {"Objects": object_identifiers})
            deleted_count+=len(object_identifiers)

        logger.info(f"Total Objects Deleted: {deleted_count}")
        return deleted_count

    def delete_bucket(self,bucket_name):
        logger.info(f"Deleting S3 bucket: {bucket_name}")
        try:
            self.s3.delete_bucket(Bucket = bucket_name)
            logger.info(f"S3 bucket deleted: {bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                logger.info(f"S3 Bucket already deleted: {bucket_name}")
                return True
            logger.error(f"Failed to delete S3 bucket: {bucket_name}: {e}")
            raise

    def cleanup_s3_bucket(self,bucket_name):
        if not bucket_name:
            logger.info("No S3 Bucket found in state")
            return False
        self.delete_bucket_object(bucket_name)
        return self.delete_bucket(bucket_name)

    
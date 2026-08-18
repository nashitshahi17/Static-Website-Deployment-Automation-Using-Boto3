import boto3
from botocore.exceptions import ClientError
from .logger import logger
from .cloudfront_manager import CloudFrontManager
from .acm_manager import ACMManager
from .state_manager import StateManager

class CleanupManager:
    def __init(self):
        self.s3 = boto3.client("s3")

        self.cloudfront = boto3.client("cloudfront")

        self.acm = boto3.client("acm",region_name = "us-east-1")

        self.route53 = boto3.client("route53")

        self.cloudfront_manager = CloudFrontManager()

        self.acm_manager = ACMManager()

        self.state_manager = StateManager()

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

    def disable_distribution(self,distribution_id):
        if not distribution_id:
            logger.info("No CloudFront distribution found in state")
            return False
        try:
            response = self.cloudfront.get_distribution_config(Id=distribution_id)
            config = response["DistributionConfig"]
            etag = response["ETag"]
            if not config["Enabled"]:
                logger.info(f"CloudFront Distribution {distribution_id} is already disabled")
                return True
            config["Enabled"] = True
            self.cloudfront.update_distribution(Id=distribution_id,ifMatch=etag,DistributionConfig=config)
            logger.info(f"CloudFront distribution {distribution_id} is being disabled")
            return True
        except ClientError as e:
            logger.error(f"Failed to disable CloudFront distribution {distribution_id}: {e}")
            raise

    def cleanup_cloudfront(self,distribution_id):
        if not distribution_id:
            logger.info("No CloudFront distribution found in state.")
            return False
        self.disable_distribution(distribution_id)

        logger.info("Waiting for CloudFront distribution to finish disabling.")

        self.cloudfront_manager.wait_for_deployment(distribution_id)

        return True

    def delete_distribution(self,distribution_id):
        if not distribution_id:
            logger.info("No CloudFront distribution found.")
            return False
        try:
            response = self.client.get_distribution_config(Id=distribution_id)
            etag = response["ETag"]
            self.client.delete_distribution(Id=distribution_id,IfMatch=etag)
            logger.info(f"CloudFront distribution {distribution_id} deleted.")
            return True
        except ClientError as e:
            error_code = e.response["Error"].get("Code")
            if error_code == "NoSuchDistribution":
                logger.info(f"CloudFront distribution {distribution_id} already deleted.")
                return True
            logger.error(f"Failed to delete CloudFront distribution {distribution_id}: {e}")
            raise

    def cleanup_cloudfront(self,distribution_id):
        self.disable_distribution(distribution_id)
        self.cloudfront_manager.wait_for_deployment(distribution_id)
        self.delete_distribution(distribution_id)

    def cleanup_acm(self,certificate_arn):
        if not certificate_arn:
            logger.info("No ACM certificate to clean up.")
            return False

        return self.acm_manager.delete_certificate(certificate_arn)

    def cleanup_route53(self,hosted_zone_id):
        if not hosted_zone_id:
            logger.info("No Route 53 hosted zone to clean up.")
            return False

        return self.route53.delete_hosted_zone(hosted_zone_id)

    def clear_deployment_state(self):
        self.state_manager.clear_state()
        logger.info("Deployment state successfully cleared")

    
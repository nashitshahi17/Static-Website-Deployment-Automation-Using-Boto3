from .config import (create_bucket_name,get_website_endpoint)
from .logger import logger
from .s3_manager import S3Manager
from .uploader import WebsiteUploader
from .cloudfront_manager import CloudFrontManager
from .state_manager import StateManager

class StaticSiteDeployer:
    def __init__(self):
        self.state_manager = StateManager()
        self.s3_manager = S3Manager()
        self.cloudfront_manager = CloudFrontManager()

    def deploy(self):
        state = self.state_manager.load()

        # S3 Bucket
        bucket_name = self._get_or_create_bucket(state)

        # Configure S3
        self.s3_manager.configure_public_access(bucket_name)
        self.s3_manager.enable_static_website(bucket_name)

        # Upload Website
        uploader = WebsiteUploader(self.s3_manager.s3)
        uploader.upload_directory(bucket_name,'website')

        # Bucket Policy 
        self.s3_manager.apply_bucket_policy(bucket_name)

        # S3 Website Endpoint
        website_endpoint = get_website_endpoint(bucket_name)

        # CloudFront
        distribution = (self._get_or_create_distribution(state,website_endpoint))

        # wait for Deployment
        deployed_distribution = (self.cloudfront_manager.wait_for_deployment(distribution["Id"]))

        # Invalidation Cache
        invalidation = (self.cloudfront_manager.create_invalidation(distribution_id=distribution["Id"],paths=["/*"]))

        if invalidation:
            self.cloudfront_manager.wait_for_invalidation(distribution_id=distribution["Id"],invalidation_id=invalidation["Id"])

        # Final Information
        cloudfront_domain = (
            deployed_distribution["DomainName"]
        )

        state["bucket_name"] = bucket_name

        state["distribution_id"] = (
            deployed_distribution["Id"]
        )

        state["cloudfront_domain"] = (
            cloudfront_domain
        )

        self.state_manager.save(state)

        logger.info("Deployment completed successfully.")

        return {
            "bucket_name": bucket_name,
            "s3_website_url": (
                f"http://{website_endpoint}"
            ),
            "distribution_id": (
                deployed_distribution["Id"]
            ),
            "cloudfront_url": (
                f"https://{cloudfront_domain}"
            )
        }

    def _get_or_create_bucket(self, state):

        bucket_name = state.get("bucket_name")

        if bucket_name:

            if self.s3_manager.bucket_exists(bucket_name):

                logger.info(
                    f"Using existing bucket: "
                    f"{bucket_name}"
                )

                return bucket_name

        bucket_name = create_bucket_name()

        self.s3_manager.create_bucket(bucket_name)

        return bucket_name

    def _get_or_create_distribution(self,state,website_endpoint):

        distribution_id = state.get("distribution_id")

        if distribution_id:

            if self.cloudfront_manager.distribution_exists(distribution_id):
                logger.info(
                    f"Using existing CloudFront "
                    f"distribution: {distribution_id}"
                )

                return self.cloudfront_manager.get_distribution(distribution_id)

            logger.warning(
                "Stored CloudFront distribution "
                "no longer exists."
            )

        distribution = self.cloudfront_manager.create_distribution(website_endpoint)
        return distribution
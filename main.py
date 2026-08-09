from src.config import (create_bucket_name, get_website_endpoint )
from src.s3_manager import S3Manager
from src.uploader import WebsiteUploader
from src.cloudfront_manager import CloudFrontManager
from src.state_manager import StateManager
# import boto3
# def main():
#     s3 = boto3.client('s3')

#     response = s3.list_buckets()

#     print("Buckets in your account: \n")

#     for bucket in response.get("Bucket",[]):
#         print(f"-{bucket['Name']}")

def main():
    state_manager = StateManager()
    state  = state_manager.load()
    manager = S3Manager()
    bucket_name = state.get('bucket_name')
    if bucket_name and manager.bucket_exists(bucket_name):
        print(f"Using existing bucket: {bucket_name}")
    else:
        bucket_name = create_bucket_name()
        manager.create_bucket(bucket_name)
        state["bucket_name"] = bucket_name
        state_manager.save(state)
    

    manager.configure_public_access(bucket_name)
    manager.enable_static_website(bucket_name)
    uploader = WebsiteUploader(manager.s3)
    uploader.upload_directory(bucket_name,"website")
    manager.apply_bucket_policy(bucket_name)

    website_endpoint = get_website_endpoint(bucket_name)
    print("Website Endpoint\n")
    print(f"http://{website_endpoint}")

    cloudfront_manager = CloudFrontManager()
    distribution_id = state.get("distribution_id")
    if distribution_id:
        try:
            distribution = (cloudfront_manager.get_distribution(distribution_id))
            print(
                f"Using existing CloudFront distribution: "
                f"{distribution_id}"
            )
        except Exception:
            distribution = (cloudfront_manager.create_distribution(website_endpoint))
            state["distribution_id"] = (distribution["Id"])
            state["cloudfront_domain"] = (distribution["DomainName"])
            state_manager.save(state)
    else:
        distribution = (cloudfront_manager.create_distribution(website_endpoint))
        state["distribution_id"] = (distribution["Id"])
        state["cloudfront_domain"] = (distribution["DomainName"])
        state_manager.save(state)

    deployed_distribution = (cloudfront_manager.wait_for_deployment(distribution["Id"]))
    cloudfront_url = (f"https://{deployed_distribution['DomainName']}")

    print("\nDeployment Complete: ")
    print("----------------------------")
    print(
        f"S3 Website: "
        f"http://{website_endpoint}"
    )
    print(
        f"CloudFront: "
        f"{cloudfront_url}"
    )

if __name__ == "__main__":
    main()
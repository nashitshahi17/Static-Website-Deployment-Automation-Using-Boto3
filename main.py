from src.deployer import StaticSiteDeployer

def main():
    deployer = StaticSiteDeployer()

    result = deployer.deploy()

    print("Deployement Complete")
    print(f"S3 Bucket : {result['bucket_name']}")

    print(f"S3 Website: {result['s3_website_url']}")

    print(f"CloudFront: {result['cloudfront_url']}")

if __name__ == "__main__":
    main()
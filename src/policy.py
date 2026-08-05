import json


def generate_public_read_policy(bucket_name):
    """
    Generate an S3 bucket policy that allows
    public read access to all objects.
    """

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

    return json.dumps(policy)
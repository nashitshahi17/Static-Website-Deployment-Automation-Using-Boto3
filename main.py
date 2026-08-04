import boto3

def main():
    s3 = boto3.client('s3')

    response = s3.list_buckets()

    print("Buckets in your account: \n")
    
    for bucket in response.get("Bucket",[]):
        print(f"-{bucket['Name']}")

if __name__ == "__main__":
    main()
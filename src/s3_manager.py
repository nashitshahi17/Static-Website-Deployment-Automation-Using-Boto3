import boto3

session = boto3.Session(profile_name='default')
iam = session.resource('iam')
for user in iam.list_all():
    print(user.username)
s3 = boto3.client('s3')


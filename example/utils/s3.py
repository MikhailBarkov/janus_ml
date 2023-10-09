import boto3


s3 = session.client(
    service_name='s3',
    endpoint_url=s3_endpoint,
    aws_access_key_id='123',
    aws_secret_access_key='12345678'
)

try:
    s3.create_bucket(Bucket='util-bucket')
except BaseException:
    pass

try:
    s3.create_bucket(Bucket='test-bucket')
except BaseException:
    pass


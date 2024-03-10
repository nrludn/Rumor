import yaml
import boto3


with open('config.yml', 'r') as stream:
    config = yaml.safe_load(stream)


s3 = boto3.client('s3',
                  aws_access_key_id=config['aws']['access_key_id'],
                  aws_secret_access_key=config['aws']['secret_access_key'],
                  region_name=config['aws']['region'])

local_file_path = 'path/to/your/local/file'
bucket_name = 'your-bucket-name'
s3_file_path = 'path/in/your/s3/bucket/filename'


s3.upload_file(local_file_path, bucket_name, s3_file_path)

print("Dosya başarıyla S3'e yüklendi.")

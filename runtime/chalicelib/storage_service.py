import boto3
import uuid
import logging
from botocore.exceptions import ClientError

class StorageService:
    def __init__(self, storage_location):
        self.client = boto3.client('s3')
        self.bucket_name = storage_location

    def get_storage_location(self):
        """returns StorageService bucket name"""
        return self.bucket_name
    
    def get_upload_url(self, prefix: str):
        """returns a presigned url for uploading an audio file"""
        # generate uuid for file name
        job_id = str(uuid.uuid4())
        key = prefix + "/" + job_id + ".mp3"
        try:
            url = self.client.generate_presigned_url(ClientMethod='put_object',
                Params = {
                    'Bucket': self.bucket_name,
                    'Key': key,
                    'ContentType': 'audio/mpeg'
                },
                ExpiresIn=300
            )
        except ClientError as e:
            logging.error(e)
            url = "Something bad happen using the client"

        return { 'url': url, 'job': job_id }
    
    def get_file(self, file_name):
        response = self.client.get_object(Bucket = self.bucket_name, Key = file_name)

        return response['Body'].read().decode('utf-8')
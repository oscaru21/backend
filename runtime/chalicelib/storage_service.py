import boto3
import uuid

class StorageService:
    def __init__(self, storage_location):
        self.client = boto3.client('s3')
        self.bucket_name = storage_location

    def get_storage_location(self):
        """returns StorageService bucket name"""
        return self.bucket_name
    
    def get_upload_url(self, prefix: str):
        """returns a presigned url for uploading a file"""
        # generate uuid for file name
        key = prefix + uuid.uuid4()
        url = self.client.generate_presigned_url(
            ClientMethod = 'put_object',
            Params = {
                'Bucket': self.bucket_name,
                'Key': key
            }
        )
        return { 'url': url }
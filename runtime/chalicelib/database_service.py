import boto3
import logging
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

class DatabaseService:
    def __init__(self, table_name):
        self.client = boto3.client('dynamodb')
        self.table_name = table_name

    def get_table_name(self):
        return self.table_name
    
    def create_new_job(self, user_id, job_id, name, to_language):
        try:
            self.client.put_item(
                TableName=self.table_name,
                Item={
                    'username': {'S': user_id},
                    'id': {'S': job_id},
                    'name': {'S': name},
                    'to_language': {'S': to_language},
                }
            )
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def get_all_items_by_username(self, user_id):
        try:
            response = self.client.query(
                TableName=self.table_name,
                KeyConditionExpression="username = :username",
                ExpressionAttributeValues={
                    ":username": {"S": user_id}
                },
            )
            print(response)
        except ClientError as e:
            logging.error(e)
            return None
        return response['Items']
    
    def upload_status(self, primary_key, sort_key, status):
        try:
            self.client.update_item(
                TableName=self.table_name,
                Key={
                    'username': {'S': primary_key},
                    'id': {'S': sort_key},
                },
                UpdateExpression="set job_status = :s",
                ExpressionAttributeValues={
                    ':s': {'S': status}
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            logging.error(e)
            return False
        return True
    
    def upload_transcript(self, primary_key, sort_key, transcript):
        try:
            self.client.update_item(
                TableName=self.table_name,
                Key={
                    'username': {'S': primary_key},
                    'id': {'S': sort_key},
                },
                UpdateExpression="set transcript = :s",
                ExpressionAttributeValues={
                    ':s': {'S': transcript}
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            logging.error(e)
            return False
        return True
    
    def upload_translation(self, primary_key, sort_key, translation):
        try:
            self.client.update_item(
                TableName=self.table_name,
                Key={
                    'username': {'S': primary_key},
                    'id': {'S': sort_key},
                },
                UpdateExpression="set translation_text = :s",
                ExpressionAttributeValues={
                    ':s': {'S': translation}
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            logging.error(e)
            return False
        return True
    
    def get_item(self, primary_key, sort_key):
        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={
                    'username': {'S': primary_key},
                    'id': {'S': sort_key},
                }
            )
        except ClientError as e:
            logging.error(e)
            return None
        return response['Item']
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
    
    def create_new_job(self, user_id, job_id):
        try:
            self.client.put_item(
                TableName=self.table_name,
                Item={
                    'username': {'S': user_id},
                    'id': {'S': job_id}
                }
            )
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def get_all_items_by_username(self, user_id):
        key_condition_expression = Key('username').eq(user_id)
        try:
            response = self.client.query(
                TableName=self.table_name,
                KeyConditionExpression=key_condition_expression,
            )
            logging.info("Getting all items by username:::::",response)
        except ClientError as e:
            logging.error(e)
            return None
        return response['Items']
    
    # def put_item(self, item):
    #     response = self.table_name.put_item(Item=item)
    #     print("Inserting element:::::",response)
    #     return response
    
    # def get_item(self, keys):
    #     response = self.table_name.get_item(keys)
    #     return response
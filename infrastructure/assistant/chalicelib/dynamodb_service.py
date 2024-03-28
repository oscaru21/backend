import boto3
from boto3.dynamodb.conditions import Key

class DynamoDBService:
    def __init__(self, table_name):
        self.client = boto3.client('dynamodb')

        key_schema = [
            {'AttributeName': 'username', 'KeyType': 'HASH'},  # Partition key
            {'AttributeName': 'id', 'KeyType': 'RANGE'}  # Sort key
        ]
        attribute_definitions = [
            {'AttributeName': 'username', 'AttributeType': 'S'},
            {'AttributeName': 'id', 'AttributeType': 'S'},
        ]
        provisioned_throughput = {
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
        try:
            response = self.client.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput=provisioned_throughput
            )
            self.table_name = boto3.resource('dynamodb').Table(table_name)
            print("Creating the table:::::",response)
        
        except self.client.exceptions.ResourceInUseException:
            self.table_name = boto3.resource('dynamodb').Table(table_name)
            print("Creating the table:::::","Table already exists")


    def get_table_name(self):
        return self.table_name

    def put_item(self, item):
        response = self.table_name.put_item(Item=item)
        print("Inserting element:::::",response)
        return response
    
    def get_item(self, keys):
        response = self.table_name.get_item(keys)
        return response
    
    def get_all_items_by_username(self, username):
        key_condition_expression = Key('username').eq(username)

        # Query the table using the key condition expression
        response = self.table_name.query(
            KeyConditionExpression=key_condition_expression
        )
        print("Getting all items by username:::::",response)
        return response

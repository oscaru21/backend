import boto3


class LoginService:
   def __init__(self, region_name='us-east-1'):
        """Initialize the DynamoDB connection."""
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table('Users')
        self.create_user_table()

   def create_user_table(self):
        """Create the DynamoDB table if it doesn't exist."""
        try:
            table = self.dynamodb.create_table(
                TableName='Users',
                KeySchema=[
                    {
                        'AttributeName': 'username',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'username',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )
            table.wait_until_exists()
            print("Table created successfully.")
        except Exception as e:
            print(f"Error creating table: {e}")

   def create_user(self, username, password):
        """Add a new user to the table."""
        try:
            response = self.table.put_item(
                Item={
                    'username': username,
                    'password': password
                }
            )
            print("User created successfully.")
            return response
        except Exception as e:
            print(f"Error adding user: {e}")
            return None

   def get_user(self, username):
        """Retrieve a user from the table by username."""
        try:
            response = self.table.get_item(Key={'username': username})
            if 'Item' in response:
                return response['Item']
            else:
                print("User not found.")
                return None
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None
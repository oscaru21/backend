import os

from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_s3 as s3

import aws_cdk as cdk

from chalice.cdk import Chalice


RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir, 'runtime')


class ChaliceApp(cdk.Stack):

    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.dynamodb_table = self._create_ddb_table()
        self.audio_bucket = self._create_audio_bucket()
        self.chalice = Chalice(
            self, 'ChaliceApp', source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                'environment_variables': {
                    'APP_TABLE_NAME': self.dynamodb_table.table_name,
                    'AUDIO_BUCKET_NAME': self.audio_bucket.bucket_name,
                }
            }
        )
        self.dynamodb_table.grant_read_write_data(
            self.chalice.get_role('DefaultRole')
        )
        self.audio_bucket.grant_read_write(
            self.chalice.get_role('DefaultRole')
        )

    def _create_audio_bucket(self):
        bucket = s3.Bucket(
            self, 'Bucket',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            cors=[
                {
                    "allowedMethods": [
                        s3.HttpMethods.PUT,
                    ],
                    "allowedOrigins": ["*"],
                    "allowedHeaders": ["*"],
                }
            ]
        )
        cdk.CfnOutput(self, 'BucketName', value=bucket.bucket_name)

        return bucket

    def _create_ddb_table(self):
        dynamodb_table = dynamodb.Table(
            self, 'AppTable',
            partition_key=dynamodb.Attribute(
                name='PK', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(
                name='SK', type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY)
        cdk.CfnOutput(self, 'AppTableName',
                      value=dynamodb_table.table_name)
        return dynamodb_table

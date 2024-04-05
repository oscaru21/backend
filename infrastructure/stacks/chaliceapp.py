import os

from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_s3 as s3, aws_sqs as sqs, aws_s3_notifications as aws_s3_noti

import aws_cdk as cdk

from chalice.cdk import Chalice


RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir, 'runtime')


class ChaliceApp(cdk.Stack):

    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.sqs_generic = self._create_sqs()
        self.dynamodb_table = self._create_ddb_table()
        self.audio_bucket = self._create_audio_bucket()
        # TODO:intanciasr table con metodo

        self.chalice = Chalice(
            self, 'ChaliceApp', source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                'environment_variables': {
                    'APP_TABLE_NAME': self.dynamodb_table.table_name,
                    'AUDIO_BUCKET_NAME': self.audio_bucket.bucket_name,
                    "SQS_GENERIC" : self.sqs_generic.queue_arn,
                    # crear env variable para el nombre de la table
                }
            }
        )
        self.dynamodb_table.grant_read_write_data(
            self.chalice.get_role('DefaultRole')
        )
        self.audio_bucket.grant_read_write(
            self.chalice.get_role('DefaultRole')
        )
        #TODO:dar permiso a chalice app para acceder a la tabla
        self.audio_bucket.add_event_notification(s3.EventType.OBJECT_CREATED, aws_s3_noti.SqsDestination(self.sqs_generic))
        #TODO:grant default role permissions for transcribe service
        self.chalice.get_role('DefaultRole').add_to_principal_policy(cdk.aws_iam.PolicyStatement(
            effect=cdk.aws_iam.Effect.ALLOW,
            actions=["transcribe:*", "translate:*", "comprehend:*"],
            resources=["*"],
        ))

    def _create_sqs(self):
        queue = sqs.Queue(self, "sqs", visibility_timeout=cdk.Duration.seconds(300))
        cdk.CfnOutput(self, 'QueueName', value=queue.queue_name)
        return queue

    def _create_audio_bucket(self):
        bucket = s3.Bucket(
            self, 'Bucket',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            cors=[
                {
                    "allowedMethods": [
                        s3.HttpMethods.PUT,
                        s3.HttpMethods.POST,
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
                name='username', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(
                name='id', type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=5,
            write_capacity=5,
            removal_policy=cdk.RemovalPolicy.DESTROY)
        cdk.CfnOutput(self, 'AppTableName',
                      value=dynamodb_table.table_name)
        return dynamodb_table
    
    # TODO:crear nuevo metodo para definir estructura de table

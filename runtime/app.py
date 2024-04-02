import os
from chalice import Chalice
from chalice import CognitoUserPoolAuthorizer

from chalicelib.storage_service import StorageService
from chalicelib.database_service import DatabaseService
import json

app = Chalice(app_name='transcriber')

# setup cognito user pool authorizer
authorizer = CognitoUserPoolAuthorizer(
    'MyPool', provider_arns=['arn:aws:cognito-idp:us-east-1:381491943332:userpool/us-east-1_qQ9hwQlhe'])

bucket_name = os.environ.get('AUDIO_BUCKET_NAME', '')
storage_service = StorageService(bucket_name)

database_table = os.environ.get('APP_TABLE_NAME', '')
database_service = DatabaseService(database_table)


# get request to get presigned url, should authenticate user with cognito and extract the user id
@app.route('/presigned-url', methods=['GET'], authorizer=authorizer, cors = True)
def get_presigned_url():
    #get user id from cognito
    user_id = app.current_request.context['authorizer']['claims']['sub']
    return storage_service.get_upload_url(user_id)

@app.on_sqs_message(queue_arn=os.environ.get('SQS_GENERIC', ''),batch_size=1)
def handle_sqs_message(event):
    for record in event:
        # extract object key from record
        body = json.loads(record.body)
        key = body['Records'][0]['s3']['object']['key']
        #remove file extension
        key = key.split('.')[0]
        user_id, job_id = key.split('/')
        # create new record in dynamo db
        database_service.create_new_job(user_id, job_id)

@app.route('/meetings', methods = ['GET'], authorizer=authorizer, cors = True)
def get_meetings():
    """get all meetings"""
    #get user id from cognito
    user_id = app.current_request.context['authorizer']['claims']['sub']
    transcriptions = database_service.get_all_items_by_username(user_id)
    return {'transcriptions': transcriptions}

    

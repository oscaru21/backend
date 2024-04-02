import os
from chalice import Chalice
from chalice import CognitoUserPoolAuthorizer

from chalicelib.storage_service import StorageService

authorizer = CognitoUserPoolAuthorizer(
    'MyPool', provider_arns=['arn:aws:cognito-idp:us-east-1:381491943332:userpool/us-east-1_qQ9hwQlhe'])


app = Chalice(app_name='transcriber')

bucket_name = os.environ.get('AUDIO_BUCKET_NAME', '')
storage_service = StorageService(bucket_name)

# get request to get presigned url, should authenticate user with cognito and extract the user id
@app.route('/presigned-url', methods=['GET'], authorizer=authorizer, cors = True)
def get_presigned_url():
    #get user id from cognito
    user_id = app.current_request.context['authorizer']['claims']['sub']
    return storage_service.get_presigned_url(user_id)

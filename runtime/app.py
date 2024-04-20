import os
from chalice import Chalice
from chalice import CognitoUserPoolAuthorizer

from chalicelib.storage_service import StorageService
from chalicelib.database_service import DatabaseService
from chalicelib.transcription_service import TranscriptionService
from chalicelib.translation_service import TranslationService

import json

app = Chalice(app_name='transcriber')

# setup cognito user pool authorizer
authorizer = CognitoUserPoolAuthorizer(
    'MyPool', provider_arns=['arn:aws:cognito-idp:us-east-1:381491943332:userpool/us-east-1_qQ9hwQlhe'])

bucket_name = os.environ.get('AUDIO_BUCKET_NAME', '')
storage_service = StorageService(bucket_name)

database_table = os.environ.get('APP_TABLE_NAME', '')
database_service = DatabaseService()

transcription_service = TranscriptionService(storage_service)
translation_service = TranslationService()

# get request to get presigned url, should authenticate user with cognito and extract the user id
@app.route('/presigned-url', methods=['POST'], authorizer=authorizer, cors = True)
def get_presigned_url():
    #get request parameters
    body = app.current_request.json_body
    to_language = body['to_language'] 
    name = body['name']

    #get user id from cognito
    user_id = app.current_request.context['authorizer']['claims']['sub']
    #generate presigned url
    url = storage_service.get_upload_url(user_id)

    # create new record in dynamo db
    database_service.create_new_job(user_id, url.get('job'), name, to_language=to_language)

    return url

@app.route('/transcribe/{job_id}', methods = ['GET'], authorizer=authorizer, cors = True)
def transcribe(job_id):
    #get user id from cognito
    user_id = app.current_request.context['authorizer']['claims']['sub']
    print(user_id)
    key = user_id + '/' + job_id + '.mp3'

    #create new record in dynamo db
    print("updating status")
    database_service.upload_status(user_id, job_id, 'uploaded')

    # start transcription job
    print("starting transcription job")
    transcript = transcription_service.transcribe_audio(key, 'en')

    database_service.upload_transcript(user_id, job_id, transcript)
    return {'transcription': transcript}


@app.route('/meetings', methods = ['GET'], authorizer=authorizer, cors = True)
def get_meetings():
    """get all meetings"""
    #get user id from cognito
    user_id = app.current_request.context['authorizer']['claims']['sub']

    if is_admin(app.current_request):
        print('Hello Admin')
        transcriptions = database_service.get_all_items()
    else:
        print("You're not an admin")
        transcriptions = database_service.get_all_items_by_username(user_id)
    return {'transcriptions': transcriptions}

@app.route('/translate/{job_id}', methods = ['GET'], authorizer=authorizer, cors = True)
def translate(job_id):
    #get user id from cognito
    user_id = app.current_request.context['authorizer']['claims']['sub']
    #get transcript from dynamo db
    item = database_service.get_item(user_id, job_id)
    transcript = item['transcript']['S']
    language = item['to_language']['S']

    #translate transcript
    translation = translation_service.translate_text(transcript, target_language=language)['translatedText']
    #save translation in dynamo db
    database_service.upload_translation(user_id, job_id, translation)

    return {'translation': translation}


#admin routes

def is_admin(request):
    groups = request.context['authorizer']['claims'].get('cognito:groups', '')
    print(groups)
    if 'ADMIN' in groups:
         return True
    else:
        return False
    
#delete transcription
@app.route('/meetings/{user_id}/{job_id}', methods = ['DELETE'], authorizer=authorizer, cors = True)
def delete_transcription(user_id, job_id):
    #check if user is admin
    if not is_admin(app.current_request):
        return {'message': 'You are not authorized to delete transcriptions'}

    #delete transcription from dynamo db
    database_service.delete_item(user_id, job_id)

    return {'message': 'Transcription deleted successfully'}


    

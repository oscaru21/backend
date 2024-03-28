from chalice import Chalice
import base64
import json
from chalicelib import dynamodb_service
## Chalice app configuration
app = Chalice(app_name='assistant')
app.debug = True

## service initialization

table = 'meetings'

dynamodb_service = dynamodb_service.DynamoDBService(table)

#####
# RESTful endpoints
#####

@app.route('/get_meetings', methods = ['POST'], cors = True)
def get_meetings():
    """get all meetings"""
    request_data = json.loads(app.current_request.raw_body)
    user_name = request_data['username']
    meetings = dynamodb_service.get_all_items_by_username(user_name)
    return meetings

@app.route('/save_meeting', methods = ['POST'], cors = True)
def put_meeting():
    """put a new meeting"""
    request_data = json.loads(app.current_request.raw_body)
    meeting = request_data
    dynamodb_service.put_item(meeting)
    return meeting
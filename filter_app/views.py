import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
import logging
from .tasks import store_comment_data
from .parsers import parse_incoming_data


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname).1s %(message)s',
    datefmt='%Y.%m.%d %H:%M:%S')

@csrf_exempt
@require_http_methods(['POST'])
def handle_request(request):
    json_data = json.loads(request.body.decode())
    data = parse_incoming_data(json_data)
    if data is None:
        return HttpResponse('Invalid incoming data', status=400)
    if data['secret'] != os.environ['VK_GROUP_SECRET_KEY']:
        return HttpResponse('Invalid secret key', status=403) 
    if data['message_type'] == 'confirmation':
        return HttpResponse(os.environ['VK_GROUP_CONFIRMATION'])
    allowed_types = ['board_post_new', 'board_post_edit', 'board_post_restore']
    if data['message_type'] in allowed_types:
        store_comment_data.delay(
            data['text'], 
            data['topic_id'], 
            data['comment_id'], 
            data['user_id'], 
            data['vk_timestamp']
        )
    return HttpResponse('ok', status=200)
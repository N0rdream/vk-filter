import os
import time
from celery import shared_task
from .vk_helpers import (
    get_members, 
    get_code_for_execute, 
    send_execute_request
)
from .models import StopWord, History
import redis
from celery.exceptions import Ignore
import json
from .parsers import parse_redis_data, parse_records
import requests


@shared_task
def store_comment_data(text, topic_id, comment_id, user_id, vk_timestamp):
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/sendMessage"
    params = {
        'chat_id': os.environ['TELEGRAM_CHAT_ID'],
        'text': f'{text}, user_id: https://vk.com/id{user_id}'
    }
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(e)
    return {
        'text': text, 
        'topic_id': topic_id,
        'comment_id': comment_id,
        'user_id': user_id,
        'vk_timestamp': vk_timestamp
    }

    
@shared_task(ignore_result=True)
def test():
    access_token = os.environ['VK_GROUP_ACCESS_TOKEN']
    api_version = os.environ['VK_API_VERSION']
    group_id = int(os.environ['VK_GROUP_ID'])
    url = os.environ['CELERY_RESULT_BACKEND']
    redis_db = redis.StrictRedis.from_url(url, db=0, decode_responses=True)
    keys = redis_db.keys()[:50]
    if not keys:
        raise Ignore
    vals = redis_db.mget(keys)
    data = parse_redis_data(keys, vals)
    broken_keys = data['broken_keys']
    if broken_keys:
        for k in broken_keys:
            redis_db.delete(k)
    groups_keys = data['groups_keys']
    if groups_keys:
        for k in groups_keys:
            redis_db.delete(k)
    records = data['records']
    if not records:
        raise Ignore
    user_ids = [str(records[k]['user_id']) for k in records]
    members = get_members(group_id, user_ids, access_token, api_version)
    if members is None:
        raise Ignore 
    stopwords = StopWord.get_stopwords()
    data = parse_records(records, members, stopwords)
    History.save_messages_non_members(data['non_members'])
    History.save_messages_have_stopword(data['have_stopword'])
    keys_for_delete = list(data['data_code'].keys()) + data['good_keys']
    for k in keys_for_delete:
        redis_db.delete(k)
    raw_code = data['data_code']
    print('raw_data', raw_code)
    if raw_code:
        code = get_code_for_execute(group_id, raw_code, access_token, api_version)
        send_execute_request(code, access_token, api_version)
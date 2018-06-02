import requests
import json


def get_members(group_id, user_ids, access_token, api_version):
    url_execute = 'https://api.vk.com/method/groups.isMember'
    params = {
        'group_id': group_id,
        'user_ids': ','.join(user_ids),
        'access_token': access_token,
        'v': api_version
    }
    response = requests.get(url_execute, params=params)
    try:
        users = response.json()['response']
    except KeyError:
        return None
    return [u['user_id'] for u in users if u['member']]
    

def construct_vkscript_comment_deleter(
        group_id, topic_id, comment_id, access_token, api_version
    ):
    params = {
        'group_id': group_id,
        'topic_id': topic_id,
        'comment_id': comment_id,
        'access_token': access_token,
        'v': api_version
    }
    return f'API.board.deleteComment({json.dumps(params)})'


def combine_lines_into_code(lines):
    return ';'.join(lines) + ';'


def get_code_for_execute(group_id, data, access_token, api_version):
    lines = []
    for k in data:
        topic_id, comment_id = data[k]
        line = construct_vkscript_comment_deleter(
            group_id, topic_id, comment_id, access_token, api_version
        )
        lines.append(line)
    return combine_lines_into_code(lines)


def send_execute_request(code, access_token, api_version):
    url_execute = 'https://api.vk.com/method/execute'
    params = {
        'code': code,
        'v': api_version,
        'access_token': access_token
    }
    r = requests.get(url_execute, params=params)
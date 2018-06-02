import json
from .text_processing import has_word, prepare_text, has_stoplist, prepare_stoplist


def parse_incoming_data(data):
    """ Incoming message:
    {
        'type': 'board_post_new', 
        'group_id': 111, 
        'object': {
            'id': 6, 
            'text': 'post 5', 
            'topic_id': 3534535345, 
            'topic_owner_id': -5345345345, 
            'from_id': 34534534534, 
            'date': 1524418424
        }, 
        'secret': 'secret'
    }
    """
    try:
        message_type = data['type']
        secret = data['secret']
        group_id = data['group_id']
    except (KeyError, TypeError):
        return None
    result = {
        'message_type': message_type,
        'group_id': group_id,
        'secret': secret
    }
    try:
        vk_timestamp = data['object']['date']
        user_id = data['object']['from_id']
        text = data['object']['text']
        topic_id = data['object']['topic_id']
        comment_id = data['object']['id']
    except KeyError:
        return result
    else:
        result['vk_timestamp'] = vk_timestamp
        result['text'] = text
        result['user_id'] = user_id
        result['topic_id'] = topic_id
        result['comment_id'] = comment_id
    return result


def parse_redis_data(keys, vals):
    records = {}
    broken_keys = [] 
    groups_keys = []
    for k, v in zip(keys, vals):
        try:
            record = json.loads(v)
        except (json.JSONDecodeError, TypeError):
            # logging
            print('json.JSONDecodeError / TypeError', k, v)
            broken_keys.append(k)
        try:
            result = record['result']
        except (KeyError, TypeError):
            # logging
            print('KeyError / TypeError', k, v)
            broken_keys.append(k)
        if int(result['user_id']) < 0:
            groups_keys.append(k)
        else:
            records[k] = result
    return {
        'records': records, 
        'broken_keys': broken_keys,
        'groups_keys': groups_keys
    }


def has_stopword(text, stopwords):
    text = prepare_text(text)
    print(text)
    for word in stopwords:
        if not word['is_list']:
            if has_word(word['phrase'], text) is not None:
                return True
        else:
            stoplist = prepare_stoplist(word['phrase'])
            if has_stoplist(stoplist, text):
                return True
    return False


def parse_records(records, members, stopwords):
    have_stopword = []
    non_members = []
    data_code = {}
    good_keys = []
    for k, v in records.items():
        if v['user_id'] not in members and len(data_code) < 25:
            non_members.append((v['vk_timestamp'], v['user_id'], v['text']))
            data_code[k] = (v['topic_id'], v['comment_id'])
        else:
            if has_stopword(v['text'], stopwords) and len(data_code) < 25:
                have_stopword.append((v['vk_timestamp'], v['user_id'], v['text']))
                data_code[k] = (v['topic_id'], v['comment_id'])
            else:
                good_keys.append(k)
    return {
        'have_stopword': have_stopword,
        'non_members': non_members,
        'data_code': data_code,
        'good_keys': good_keys
    }
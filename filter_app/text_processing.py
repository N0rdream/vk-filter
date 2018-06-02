import re


def has_word(word, text):
    regexpr = r'{}[^a-zа-я]*\b'.format(word)
    pattern = re.compile(regexpr)
    return pattern.search(text)


def prepare_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zа-я0-9\s]', '', text)
    text = text.replace('3', 'е')
    text = text.replace('0', 'о')
    text = text.replace('a', 'а')
    text = text.replace('e', 'е')
    text = text.replace('o', 'о')
    text = text.replace('m', 'м')
    text = text.replace('vip', 'вип')
    text = text.replace('p', 'р')
    text = text.replace('ё', 'е')
    return text


def has_stoplist(stoplist, text):
    for word in stoplist:
        if word not in text:
            return False
    return True


def prepare_stoplist(stoplist):
    return ''.join(stoplist.split()).split(',')
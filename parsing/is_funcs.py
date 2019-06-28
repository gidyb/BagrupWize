import random
from parsing import keywords

def is_relevant_to_subject(msg):
    return get_num_keywords(msg) > 0

def is_informative(is_relevant_to_subject, is_question):
    return is_relevant_to_subject and not is_question

def get_num_keywords(msg,keywords_type):
    return keywords.count_words(msg, keywords_type, keywords_type)

def is_question(msg,group_type):
    num_question_words = keywords.count_words(msg, keywords.QUESTION, group_type) > 0
    # We found out ? is enough...
    return '?' in msg

def is_encourage(msg,group_type):
    return keywords.count_words(msg, keywords.ENCOURAGE,group_type) > 0

def is_acknowledge(msg,group_type):
    return keywords.count_words(msg, keywords.ACK,group_type) > 0

def text_length(msg):
    return len(msg)

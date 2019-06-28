#!/usr/bin/env python
import os
import logging
import sys
import argparse
from parsing import is_funcs as is_funcs
import parsing.csv_reader as cr
import analysis.analyze as an

logger = logging.getLogger('ExportParser')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s - %(message)s')

anonymous_names = {}
global last_student_id
global last_teacher_id

SPAM_PHRASES = ['You added', 'You created', 'You changed', 'Messages to this group','changed the group description',
                'changed the subject from', 'changed this group', 'added', 'changed their phone','You removed']

basic_cols = 'date,time_of_day,id,sender_name,text_length'
heb_cols = 'msg_text'
is_cols = 'num_keywords,is_relevant_to_subject,is_question,is_informative,is_encourage,is_ack,is_left_group,is_media_omitted'

MAX_TEXT_LENGTH = 500

def get_standard_file_name(raw_path):
    # Rename file to standard format (levaing original
    filename = os.path.split(raw_path)[1]
    new_filename = filename.split('_')[1]
    new_path = os.path.join(os.path.split(raw_path)[0],new_filename)
    return new_path


def is_start_msg(line):
    return '/2019' in line


def get_name_and_msg_txt(name_and_text):
    if ':' in name_and_text:
        colon_idx = name_and_text.index(':')
        sender_name = name_and_text[:colon_idx]
        msg_txt = name_and_text[colon_idx+1:]
        if 'Media omitted' in msg_txt:
            return sender_name, 'MEDIA_OMITTED','False','True'
        else:
            return sender_name, msg_txt,'False','False'
    elif 'left' in name_and_text:
        return name_and_text.replace('left',''), 'LEFT_GROUP','True','False'
    else:
        return 'UNKNOWN_FORMAT',name_and_text,'False','False'


def get_anonym_sender(sender_name, teacher_name,other_teachers_name):
    global last_teacher_id, last_student_id

    if sender_name in anonymous_names:
        # Known sender
        return anonymous_names[sender_name]

    anonym_name = None
    if teacher_name in sender_name:
        anonym_name = 'MAIN_TEACHER'

    # Check for other teachers
    for other_teacher in other_teachers_name:
        if other_teacher in sender_name:
            last_teacher_id += 1
            anonym_name = 'TEACHER_{}'.format(last_teacher_id)

    if anonym_name is None:
        # Still haven't found a match => a new student
        last_student_id += 1
        anonym_name = 'STUDENT_{}'.format(last_student_id)

    anonymous_names[sender_name] = anonym_name
    return anonym_name


def parse_msg_to_csv(id, msg, teacher_name,other_teachers_names, keywords_type):
    csv_msg = msg

    # Remove all new_lines and add one in the end
    csv_msg = csv_msg.replace('\n','')

    date = csv_msg[:10]
    time = csv_msg[12:17]
    sender_name, msg_text,is_left_group,is_media_omitted = get_name_and_msg_txt(csv_msg[20:])

    anonym_sender = get_anonym_sender(sender_name,teacher_name,other_teachers_names)

    msg_text = msg_text.replace(',',';')
    text_length = str(len(msg_text))

    num_keywords = is_funcs.get_num_keywords(msg_text,keywords_type)
    is_relevant_to_subject = str(num_keywords>0)
    num_keywords = str(num_keywords)
    is_question = str(is_funcs.is_question(msg_text,keywords_type))
    is_informative = str(is_funcs.is_informative(is_relevant_to_subject=='True', is_question=='True'))
    is_encourage = str(is_funcs.is_encourage(msg_text,keywords_type))
    is_ack = str(is_funcs.is_acknowledge(msg_text,keywords_type))

    if int(text_length) < MAX_TEXT_LENGTH:
        csv_msg_no_heb = '{}\n'.format(
            ','.join([date,time,str(id),anonym_sender,text_length,num_keywords,is_relevant_to_subject,is_question,
                      is_informative,is_encourage,is_ack,is_left_group,is_media_omitted]))

        csv_msg = '{},{}\n'.format(csv_msg_no_heb[:-1],msg_text)
    else:
        csv_msg_no_heb = ''
        csv_msg = ''

    return csv_msg, csv_msg_no_heb, anonym_sender, msg_text


def is_line_relevant(line, spam_names):
    for phrase in SPAM_PHRASES:
        if phrase in line:
            return False
    for name in spam_names:
        if name in line:
            return False
    return True


def extract_csv_file(standard_name_path, teacher_name, other_teachers_names, spam_names, keywords_type):
    logger.info('Starting extracting csv from {}'.format(standard_name_path))

    with open(standard_name_path, 'r') as file:
        raw_data = file.readlines()

    all_cols = '{},{},{}\n'.format(basic_cols,is_cols,heb_cols)
    all_cols_no_heb = '{},{}\n'.format(basic_cols,is_cols)

    csv_lines_list = [all_cols]
    csv_lines_no_heb_list = [all_cols_no_heb]

    cur_msg = None
    for id, line in enumerate(raw_data):
        if is_line_relevant(line, spam_names):
            if is_start_msg(line):
                if cur_msg is not None:
                    # End previous msg
                    csv_msg, csv_msg_no_heb, anonym_sender, msg_text = \
                        parse_msg_to_csv(id,cur_msg,teacher_name,other_teachers_names,keywords_type)
                    csv_lines_list.append(csv_msg)
                    csv_lines_no_heb_list.append(csv_msg_no_heb)
                cur_msg = line
            elif cur_msg is None:
                cur_msg = line
            else:
                cur_msg += '   {}'.format(line)

    csv_file_path = standard_name_path + '.csv'
    with open(csv_file_path, 'w') as csv_file:
        csv_file.writelines(csv_lines_list)

    csv_no_heb_file_path = standard_name_path + '.no_heb.csv'
    with open(csv_no_heb_file_path, 'w') as csv_file:
        csv_file.writelines(csv_lines_no_heb_list)

    return csv_no_heb_file_path


def write_std_and_file(f,str):
    # print(str)
    f.writelines('{}\n'.format(str))

def extract_names(export_file):
    names_file = '{}_names.csv'.format(export_file)
    with open(names_file, 'w') as f:
        write_std_and_file(f, 'name,anonymous_name')
        for name, anonym_name in anonymous_names.items():
            write_std_and_file(f, '{},{}'.format(name, anonym_name))


def init():
    global last_teacher_id, last_student_id
    last_student_id = -1
    last_teacher_id = -1


def validate_export_dir(export_dir_path):
    export_txt_filename = None
    params_filename = None
    for filename in os.listdir(export_dir_path):
        if filename.startswith('WhatsApp') and filename.endswith('txt'):
            export_txt_filename = filename
        elif filename == 'params.txt':
            params_filename = filename

    assert export_txt_filename is not None and params_filename is not None, \
        'Dir {} must include WhatsApp export and params.txt file'.format(export_dir_path)

    export_file = os.path.join(export_dir_path,export_txt_filename)

    # csv_file = '{}.csv'.format(export_file)
    # if os.path.exists(csv_file):
    #     logger.warning('CSV files already exist, removing them')
    #     shutil.rmtree(csv_file)

    params_file = os.path.join(export_dir_path,params_filename)
    with open(params_file,'r') as f:
        params = f.readlines()

    return export_file, params


def parse_params(params):
    group_type = params[0].split('=')[1][:-1]
    group_code = params[1].split('=')[1][:-1]
    spam_names = params[2].split('=')[1][:-1]
    spam_names = parse_list_param(spam_names)
    teacher_name = params[3].split('=')[1][:-1]
    other_teacher_names = params[4].split('=')[1][:-1]
    other_teacher_names = parse_list_param(other_teacher_names)
    return group_type,group_code,spam_names,teacher_name,other_teacher_names

def parse_list_param(param):
    if param == 'NONE':
        param = []
    else:
        param = param.split(',')
    return param


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('export_dir_path', help='Full path of the export dir')
    args = parser.parse_args()

    export_dir_path = args.export_dir_path
    export_file, params_lines = validate_export_dir(export_dir_path)

    group_type, group_code, spam_names, teacher_name, other_teachers_names = parse_params(params_lines)

    logger.info('Analyzing {} group with code {}'.format(group_type, group_code))

    init()

    csv_file = extract_csv_file(export_file, teacher_name, other_teachers_names, spam_names, group_type)

    extract_names(export_file)

    pickle_file = cr.csv2dict(csv_file)

    an.analyze(pickle_file, export_dir_path)

    logger.info('All Done. Enjoy Bagrup-wize output! :)')





if __name__ == '__main__':
    main()

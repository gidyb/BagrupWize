import csv
from datetime import datetime
import pickle

def csv2dict(filename):
    chat = []
    col_num = 0
    with open(filename) as csvfile:
        csv_chat = csv.reader(csvfile, delimiter=',')
        for row in csv_chat:
            if row[0] == 'date':
                col_num = len(row)
                msg_field = ['']*col_num
                for index, field in enumerate(row):
                    msg_field[index] = field
            else:
                msg = {}
                raw_date = row[0].split('/')
                raw_time = row[1].split(':')
                date_time = datetime(int(raw_date[2]), int(raw_date[1]), int(raw_date[0]), int(raw_time[0]), int(raw_time[1]))
                # tag = msg_tagger(row[3])
                for index, field in enumerate(msg_field):
                    value = row[index]
                    if index == 0:
                        pass
                    elif index == 1:
                        msg.update({'date_time': date_time})
                    else:
                        if index < col_num:
                            msg.update({msg_field[index]: value})
                chat.append(msg)
    pickle.dump(chat, open(filename + '.p', "wb"))
    return filename + '.p'
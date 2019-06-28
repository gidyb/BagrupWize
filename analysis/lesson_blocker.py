import bisect
import datetime, time

'''
IMPORTANT!!!!!!!!!!
this module only deals with arrays given in the form of its class
use the functions to convert your arrays into the format
'''


class Message:
    def __init__(self, msg):
        self.msg = msg

    def __gt__(self, other):
        return self.msg.date_time > other.date_time

    def __lt__(self, other):
        return self.date_time < other.date_time

    def __eq__(self, other):
        return self.date_time == other.date_time


'''assuming all classes are 1 hour in length'''
lesson_times = []



'''
add the time a new lesson occurred in the group
'''
def add_lesson_time(yr, mnth, day, hr, min):
    time = datetime.datetime(yr,mnth, day, hr, min,0,0)
    bisect.insort_left(lesson_times, time)

'''start time and end time of the lesson'''
def get_lesson_time(date):
    start = None
    end = None
    for c in lesson_times:
        if (c.year == date.year) and (c.month == date.month) and (c.day == date.day):
            start = c
            end = start + datetime.timedelta(hours=1)
    return start, end

'''
get all messages that occurred in certain timeframe
'''
def get_time_frame(conversation, start, end):
    return [x for x in conversation if x.msg["date_time"]>=start and x.msg["date_time"]<=end]

'''
get both lesson message blocks and blocks between lessons
'''
'''def get_all_blocks(conversation):
    if len(lesson_times) == 0:
        return [{"block":conversation, "is_lesson":False}]
    blocks = [{"block":get_time_frame(conversation, conversation[0].msg["date_time"], lesson_times[0]), "is_lesson":False}]
    for i in lesson_times:
        blocks.append({"block":get_time_frame(conversation, lesson), "is_lesson":False})
    pass #todo'''

'''
is the message in the timeframe of the lesson
works with regular format
'''
def in_lesson(msg, lesson_date=None):
    if lesson_date == None:
        for l in lesson_times:
            if(in_lesson(msg, l)):
                return True
        return False
    start, end = get_lesson_time(lesson_date)
    return msg["date_time"] > start and msg["date_time"] < end

'''
add tag to messages
works with regular format

'''
def tag_all(conversation):
    for m in conversation:
        m["in_lesson"] = in_lesson(m)

'''
get all messages from certain class
'''
def get_lesson_block(conversation, date):
    #find lesson time
    return [x for x in conversation if in_lesson(x.msg, date)]

'''
get message blocks for all the lessons
'''
def get_all_lesson_blocks(conversation):
    blocks = []
    for c in lesson_times:
        blocks.append({"block":get_lesson_block(conversation, c), "is_lesson":True})
    return blocks


'''functions for converting data to the type used by the module'''
def dict2class_array(dict_conv):
    class_conv = []
    for msg in dict_conv:
        class_conv.append(Message(msg))
    return class_conv

def class2dict_array(class_conv):
    dict_conv = []
    for msg in class_conv:
        dict_conv.append(msg.msg)
    return dict_conv

if __name__ == '__main__':
    conversation = []

    print("creating list...")

    for d in range(1,8):
        #add class times
        if d % 3 == 0:
            add_lesson_time(2019, 6, d, 19, 0)
        for i in range(10):
            time = datetime.datetime.now() + datetime.timedelta(minutes=i)
            time.replace(day=d, hour=19)
            conversation.append({"meta_data":"bob", "date_time":time, "message":"haha"})


    print("analyzing...")

    for m in conversation:
        print(m)

    my_conv = dict2class_array(conversation)



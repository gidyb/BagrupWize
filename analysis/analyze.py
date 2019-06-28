import pickle
import csv
import datetime
import os
import sys
import analysis.lesson_blocker as lb
import analysis.student_analysis as sa
import logging

logger = logging.getLogger('Analyze')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s - %(message)s')

def analyze(path_to_file, dir_path):
    logger.info('Starting to analyze {}'.format(path_to_file))
    #open input pickle file
    conv = pickle.load(open(path_to_file, "rb"))

    #add class times
    param_file = open(os.path.join(dir_path, "params.txt"), 'r')
    line = param_file.readline()
    while(not line == "lesson times:\n"):
        line = param_file.readline()
    line = param_file.readline()
    while (not "end" in line):
        d = line.split(",")
        lb.add_lesson_time(int(d[0]), int(d[1]), int(d[2]), int(d[3]), int(d[4]))
        line = param_file.readline()

    lb.tag_all(conv)

    #fix data
    first = True
    for i in range(len(conv)):
        m=conv[i]
        if m["is_ack"] == "False":
            m["is_ack"] = False
        else:
            m["is_ack"] = True
        if m["is_relevant_to_subject"] == "False":
            m["is_relevant_to_subject"] = False
        else:
            m["is_relevant_to_subject"] = True
        if m["is_question"] == "False":
            m["is_question"] = False
        else:
            m["is_question"] = True
        if m["is_informative"] == "0":
            m["is_informative"] = False
        else:
            m["is_informative"] = True
        if m["is_encourage"] == "False":
            m["is_encourage"] = False
        else:
            m["is_encourage"] = True
        if first:
            first = False
            continue
        #under assumption that media that is sent after long period of silence is a question
        if m["is_media_omitted"]:
            if m["date_time"] > conv[i - 1]["date_time"] + datetime.timedelta(minutes=30):
                m["is_question"] = True

    #get analysis per student
    analys = []
    for s in range(100):
        analys.append((sa.get_student_analysis(conv, "STUDENT_"+str(s)),s))

    try:
        sa.plot_students_graphs(conv, 1, 500, dir_path)
    except:
        logger.error('Plotting trends failed!')

    #write all student analysis to csv file
    students_file = os.path.join(dir_path,'student.csv')
    with open(students_file,'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['Name', 'encourage - total','encourage - in lesson','encourage - not lesson',
                             'answers - total','answers - in lesson','answers - not lesson',
                             'questions - total','questions - in lesson','questions - not lesson',
                             'acknowledgements - total','acknowledgements - in lesson','acknowledgements - not lesson',
                             'assists - total','assists - in lesson','assists - not lesson',
                             'activity - total','aactivity - in lesson','activity - not lesson'])
        for a in reversed(sorted(analys, key=lambda a: a[0]["active"][0])):
            filewriter.writerow(["STUDENT_"+str(a[1]), a[0]['encourage'][0], a[0]['encourage'][1],a[0]['encourage'][2],
                                 a[0]['answ'][0], a[0]['answ'][1],a[0]['answ'][2],
                                 a[0]['quest'][0],a[0]['quest'][1],a[0]['quest'][2],
                                 a[0]['ack'][0], a[0]['ack'][1], a[0]['ack'][2],
                                 a[0]['helper'][0], a[0]['helper'][1], a[0]['helper'][2],
                                 a[0]['active'][0], a[0]['active'][1], a[0]['active'][2]])




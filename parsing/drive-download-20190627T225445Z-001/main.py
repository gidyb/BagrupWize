import pickle
import datetime
import lesson_blocker, student_analysis

if __name__ == '__main__':
    conv = pickle.load(open("8706.txt.no_heb.csv.p","rb"))

    # add class times
    class_conv = lesson_blocker.dict2class_array(conv)
    lesson_blocker.add_lesson_time(2019, 3, 3, 20, 0)
    lesson_blocker.tag_all(conv)


    # print(len(conv))
    chunks = []
    n = 100

    for m in conv:
        m["is_ack"] = False
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
    # student_analysis.get_change_in_student(conv, 'STUDENT_8', 3, 0.5)
    student_analysis.plot_students_graphs(conv,1,50)
    for i in range(0, len(conv), n):
        chunks.append(conv[i:i+n])
        # print(conv[i:i+n])
        # print(student_analysis.get_student_analysis(conv[i:i+n],"MAIN_TEACHER"))



'''
all functions return in format total, in_lesson, out_lesson
'''

import numpy as np
from matplotlib import pyplot as plt

def get_num_encouragement(conversation, name):
    total = 0
    in_lesson = 0

    for m in conversation:
        if m["sender_name"] == name:
            if m["is_encourage"]:
                total += 1
                if m["in_lesson"]:
                    in_lesson += 1

    return total, in_lesson, total - in_lesson

def get_num_answers(conversation, name):
    total = 0
    in_lesson = 0

    for m in conversation:
        if m["sender_name"] == name:
            if m["is_relevant_to_subject"] and not m["is_question"]:
                total += 1
                if m["in_lesson"]:
                    in_lesson += 1

    return total, in_lesson, total - in_lesson

def get_num_questions(conversation, name):
    total = 0
    in_lesson = 0

    for m in conversation:
        if m["sender_name"] == name:
            if m["is_relevant_to_subject"] and m["is_question"]:
                total += 1
                if m["in_lesson"]:
                    in_lesson += 1

    return total, in_lesson, total - in_lesson

def get_helper_score(conv, name):
    sub_conv_len = 1000
    score = 0
    in_lesson = 0
    #find question answer pairs BY STUDENTS
    for i in range(len(conv)):
        if not (conv[i]["is_question"] and conv[i]["is_relevant_to_subject"]):
            continue
        asker = conv[i]["sender_name"]
        #find whether student gave answer
        for j in range(sub_conv_len):
            if conv[i]["sender_name"] == asker and conv[i]["is_ack"]:
                break
            if conv[i]["sender_name"] == name and conv[i]["is_relevant_to_subject"] and not conv[i]["is_question"]:
                score += 1
                if conv[i]["in_lesson"]:
                    in_lesson += 1
                break
    return score, in_lesson, score - in_lesson



def get_participation_score(conversation, name):
    total = 0
    in_lesson = 0

    for m in conversation:
        if m["sender_name"] == name:
            if m["is_relevant_to_subject"] or m["is_ack"] or m["is_encourage"]:
                total += 1
                if m["in_lesson"]:
                    in_lesson += 1

    return total, in_lesson, total - in_lesson

def get_student_graphs(conversation, name, periods_num, min_slope):
    conversation_samples = sample_conversation(conversation, periods_num)
    questions = []
    samples = []
    encouragements = []
    answers = []
    participation =[]
    participation_total = []
    for index, sample in enumerate(conversation_samples):
        if index < len(conversation_samples):
            # print(len(conversation_samples[0]))
            samples.append(index)
            questions.append(get_num_questions(sample, name))
            encouragements.append(get_num_encouragement(sample, name))
            answers.append(get_num_answers(sample, name))
            participation.append(get_participation_score(sample, name))

    for tup in participation:
        participation_total.append(tup[0])
    z = np.polyfit(samples, participation_total, 1)

    if abs(z[0]) > min_slope:
        if z[0] > 0:
            return participation_total, 'STUDENT_ACTIVITY_INC'
        else:
            return participation_total, 'STUDENT_ACTIVITY_DEC'
    else:
        return participation_total, 'NO_TREND'
    # if strictly_increasing(participation):
    #     return 'STUDENT_ACTIVITY_INC'
    # elif strictly_decreasing(participation):
    #     return 'STUDENT_ACTIVITY_DEC'
    # else:
    #     return 'NO_TREND'
    # return samples, questions, encouragements, answers, participation

def plot_students_graphs(conversation, min_student_ID, max_student_ID):
    student_graphs = dict()
    plt.figure()
    legend_labels = []
    for i in range(min_student_ID, max_student_ID):
        student_name = 'STUDENT_' + str(i)
        students_graphs_results = get_student_graphs(conversation, student_name, 4, 3)
        if students_graphs_results[1] != 'NO_TREND':
            print(student_name + ':' + students_graphs_results[1])
            d1 = {student_name: students_graphs_results[0]}
            student_graphs.update(d1)
            plt.plot(student_graphs[student_name])
            legend_labels.append(student_name)
    plt.legend(legend_labels)
    plt.ylabel('Messages of student')
    plt.title('Important trends in messages of students')
    plt.savefig('important_trends.jpg', dpi=800)
    plt.show()

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def sample_conversation(conversation, N_samples):
    conv = get_conversation_without_teacher(conversation)
    num_of_msg_in_conversation = len(conv)
    chunks_size = num_of_msg_in_conversation//N_samples
    return list(chunks(conv, chunks_size))

def get_conversation_without_teacher(conversation):

    conv_without = []
    for msg in conversation:
        if 'STUDENT' in msg["sender_name"]:
            conv_without.append(msg)
    return conv_without


functions = {"encourage":get_num_encouragement,
             "answ":get_num_answers,
             "quest":get_num_questions,
             "helper":get_helper_score,
             "active":get_participation_score}

'''get overall analysis for student'''
def get_student_analysis(conversation, name):
    analysis = {}
    for f in functions:
        analysis[f] = functions[f](conversation, name)
    return analysis
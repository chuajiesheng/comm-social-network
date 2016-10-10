import sys
import glob
import os
import csv
import json

folder = 'input'
file_type = '*.csv'
output_folder = 'output'


class Student:
    id = None
    conversed_with = []
    met_facetoface = []
    knowledge_source = []
    personal_advice = []
    hangout = []
    goto_in_trouble = []
    trust = []
    attributes = [conversed_with, met_facetoface, knowledge_source, personal_advice, hangout, goto_in_trouble, trust]

    def __init__(self, id):
        self.id = id

    def add_response(self, question, to, strength):
        # question - 1 due to indexing
        self.attributes[question - 1].append((to, strength))


def find_all_csv(folder):
    search_path = folder + os.sep + file_type
    print('# Searching: {}'.format(search_path))

    f = glob.glob(search_path)
    print('# Found: {}'.format(f))

    return f


def parse_row(student, row):
    for k in row.keys():
        key_parts = k.split('_')

        if len(key_parts) != 3:
            # need to be in Q<question_id>_<person_id>_Rank
            continue

        if not row[k].strip():
            # ignore empty cell
            continue

        if key_parts[2] == 'Group':
            # columns with Group does not provide value
            continue

        question_id = int(key_parts[0][1:])
        if question_id == 9:
            # due to a bug in the creation of the questionaire
            question_id = 8

        student_id = int(key_parts[1])
        print('## Adding response: from {}, to {}, for {}, with {}'.format(student.id, student_id, question_id, row[k]))
        # question_id - 1 because Q1 is used to denote the person answering the question
        student.add_response(question_id - 1, student_id, int(row[k]))


def read_csv(filename):
    students = dict()

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id = row['Q1']

            if not id.strip():
                continue

            student = Student(id)
            parse_row(student, row)

            students[id] = student

    return students


def output_json(filename, students):
    output_file = output_folder + os.sep + filename + '.json'
    print('# Output to: {}'.format(output_file))


def main():
    data_files = find_all_csv(folder)
    for f in data_files:
        print('Reading: {}'.format(f))
        students = read_csv(f)
        filename = f[len(folder + os.sep):-len('.csv')]
        output_json(filename, students)


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
        sys.exit(1)

    main()
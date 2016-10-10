import sys
import glob
import os
import csv
import json
import copy

folder = 'input'
output_folder = 'output'
file_type = '*.csv'


class Survey:

    conversed_with = []
    met_facetoface = []
    knowledge_source = []
    personal_advice = []
    hangout = []
    goto_in_trouble = []
    trust = []
    attributes = [conversed_with, met_facetoface, knowledge_source, personal_advice, hangout, goto_in_trouble, trust]

    def __init__(self):
        pass

    def parse_row(self, row):
        source_id = row['Q1']

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

            destination_id = int(key_parts[1])
            print('## Adding response: from {}, to {}, for {}, with {}'.format(source_id, destination_id, question_id, row[k]))
            # question_id - 1 because Q1 is used to denote the person answering the question
            self.add_response(question_id - 1, source_id, destination_id, int(row[k]))

    def add_response(self, question, source, destination, strength):
        # question - 1 due to indexing
        # format: {source: "Microsoft", target: "Amazon", type: "relationship", strength: 1}
        record = {"source": "student_{}".format(source), "target": "student_{}".format(destination),
                  "type": "relationship", "strength": strength}
        self.attributes[question - 1].append(record)

    def to_json(self, base_filename):
        for question_id, response in enumerate(self.attributes):
            dest = output_folder + os.sep + base_filename + '_Q' + str(question_id + 2) + '.json'
            print('# Output to: {}'.format(dest))
            print('# Number of edges: {}'.format(len(response)))
            with open(dest, 'w') as out:
                out.write('var links = ')
                json.dump(response, out)
                out.write(';')


def find_all_csv(search_path):
    search_path = search_path + os.sep + file_type
    print('# Searching: {}'.format(search_path))

    f = glob.glob(search_path)
    print('# Found: {}'.format(f))

    return f


def read_csv(filename):
    survey = Survey()

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not row['Q1'].strip():
                continue

            survey.parse_row(row)

    return survey


def output_json(filename, survey):
    survey.to_json(filename)


def copy_base_html(base_filename, survey):
    f = open('base/base.html', 'r')
    base_file_data = f.read()
    f.close()

    no_of_qns = len(survey.attributes)
    for question_id in range(2, 2 + no_of_qns):
        json_file = base_filename + '_Q' + str(question_id) + '.json'
        dest_filename = output_folder + os.sep + base_filename + '_Q' + str(question_id) + '.html'

        html = copy.deepcopy(base_file_data)
        html = html.replace("data.json", json_file)

        print('# Output to: {}'.format(dest_filename))
        f = open(dest_filename, 'w')
        f.write(html)
        f.close()


def main():
    data_files = find_all_csv(folder)
    for f in data_files:
        print('Reading: {}'.format(f))
        survey = read_csv(f)
        filename = f[len(folder + os.sep):-len('.csv')]
        output_json(filename, survey)
        copy_base_html(filename, survey)


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
        sys.exit(1)

    main()
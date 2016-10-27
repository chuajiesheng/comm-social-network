import sys
import glob
import os
import csv
import json
import copy
import random
import code
import networkx as nx

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

    student_mapping = dict()
    graphs = dict()

    def __init__(self):
        pass

    def to_rand(self, id):
        student_id = int(id)

        if student_id in self.student_mapping.keys():
            return self.student_mapping[student_id]

        new_id = random.randint(student_id * 50, (student_id * 500) - 1)
        self.student_mapping[student_id] = new_id
        print('# From {} to {}'.format(id, new_id))

        return self.student_mapping[student_id]

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
            # question_id - 1 because Q1 is used to denote the person answering the question
            self.add_response(question_id - 1, self.to_rand(source_id), self.to_rand(destination_id), int(row[k]))

    def add_response(self, question, source, destination, strength):
        # question - 1 due to indexing
        # format: {source: "Microsoft", target: "Amazon", type: "relationship", strength: 1}
        s = "student_{}".format(source)
        d = "student_{}".format(destination)
        record = {"source": s, "target": d,
                  "type": "relationship", "strength": strength}
        self.attributes[question - 1].append(record)

        if question not in self.graphs.keys():
            self.graphs[question] = nx.DiGraph()

        self.graphs[question].add_edge(s, d, weight=strength)

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


def analyse(survey):
    graphs = survey.graphs

    for k in graphs.keys():
        print('# Analysing Q{}'.format(int(k) + 1))
        g = graphs[k]
        degree(g)
        closeness(g)
        betweenness(g)
        edge_betweenness(g)
        number_weakly_connected_components(g)
        density(g)
        # code.interact(local=dict(globals(), **locals()))


def density(g):
    d = nx.density(g)
    print('## Density: {}'.format(d))


def number_weakly_connected_components(g):
    # Return the number of connected components in G. For directed graphs only.
    n = nx.number_weakly_connected_components(g)
    print('## Number_weakly_connected_components: {}'.format(n))


def edge_betweenness(g):
    # Betweenness centrality of an edge e is the sum of the fraction of all-pairs shortest paths that pass through e
    e = nx.edge_betweenness_centrality(g, normalized=False)
    e_sorted = [(k, e[k]) for k in sorted(e, key=e.get, reverse=True)]
    first = e_sorted[0]
    last = e_sorted[len(e_sorted) - 1]
    print('## Highest edge_betweenness_centrality: {} with {}'.format(first[0], first[1]))
    print('## Lowest edge_betweenness_centrality: {} with {}'.format(last[0], last[1]))


def betweenness(g):
    # Betweenness centrality of a node v is the sum of the fraction of all-pairs shortest paths that pass through v
    b = nx.betweenness_centrality(g, normalized=False)
    b_sorted = [(k, b[k]) for k in sorted(b, key=b.get, reverse=True)]
    first = b_sorted[0]
    last = b_sorted[len(b_sorted) - 1]
    print('## Highest betweenness_centrality: {} with {}'.format(first[0], first[1]))
    print('## Lowest betweenness_centrality: {} with {}'.format(last[0], last[1]))


def closeness(g):
    # Closeness centrality [1] of a node u is the reciprocal of the sum of the shortest path distances from u to all n-1 other nodes.
    c = nx.closeness_centrality(g, normalized=False)
    c_sorted = [(k, c[k]) for k in sorted(c, key=c.get, reverse=True)]
    first = c_sorted[0]
    last = c_sorted[len(c_sorted) - 1]
    print('## Highest closeness_centrality: {} with {}'.format(first[0], first[1]))
    print('## Lowest closeness_centrality: {} with {}'.format(last[0], last[1]))


def degree(g):
    # The degree centrality for a node v is the fraction of nodes it is connected to
    d = nx.degree_centrality(g)
    d_sorted = [(k, d[k]) for k in sorted(d, key=d.get, reverse=True)]
    first = d_sorted[0]
    last = d_sorted[len(d_sorted) - 1]
    print('## Highest degree_centrality: {} with {}'.format(first[0], first[1]))
    print('## Lowest degree_centrality: {} with {}'.format(last[0], last[1]))


def main():
    data_files = find_all_csv(folder)
    for f in data_files:
        print('Reading: {}'.format(f))
        survey = read_csv(f)
        filename = f[len(folder + os.sep):-len('.csv')]
        output_json(filename, survey)
        copy_base_html(filename, survey)
        analyse(survey)


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
        sys.exit(1)

    main()
import uppaalpy
import os
from uppaalpy import path_analysis as p

testcase_dir = "lib/uppaalpy/path_tests/testcases/"

def list_nta_in_dir(directory):
    return [directory.strip('/') + '/' + x \
            for x in os.listdir(directory) if x.endswith('.xml')]

def good_nta():
    file_path = testcase_dir + "good_nta"
    return list_nta_in_dir(file_path)

def reachable_nta():
    file_path = testcase_dir + "path_realizable"
    return list_nta_in_dir(file_path)

def not_reachable_nta():
    file_path = testcase_dir + "path_not_realizable"
    return list_nta_in_dir(file_path)

def path_exists():
    file_path = testcase_dir + "path_exists"
    return list_nta_in_dir(file_path)

def path_not_exists():
    file_path = testcase_dir + "path_not_exists"
    return list_nta_in_dir(file_path)

def generator_ntas():
    file_path = "examples/generator"
    return list_nta_in_dir(file_path)

def epsilon_tests():
    file_path = testcase_dir + "epsilon_tests"
    return list_nta_in_dir(file_path)

def read_file(fp):
    return uppaalpy.NTA.from_xml(fp)

def write_to_file(nta):
    return nta.to_file('/tmp/out.xml')

def get_path_from_query_comment(nta):
    path_string = nta.queries[0].comment
    index = int(nta.queries[1].comment)
    res = []
    state = True
    for word in path_string.split():
        if state:
            state = False
            res.append(word)
        else:
            state = True
            res.append(int(word))
    return p.convert_to_path(nta.templates[index], res)

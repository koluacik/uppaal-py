import os
import uppaalpy
from uppaalpy import path as p

def list_nta_in_dir(directory):
    return [directory.strip('/') + '/' + x \
            for x in os.listdir(directory) if x.endswith('.xml')]

def broken_xml():
    file_path = "tests/broken_xml"
    return list_nta_in_dir(file_path)

def broken_nta():
    file_path = "tests/broken_nta"
    return list_nta_in_dir(file_path)

def good_nta():
    file_path = "tests/good_nta"
    return list_nta_in_dir(file_path)

def reachable_nta():
    file_path = "tests/path_realizable"
    return list_nta_in_dir(file_path)

def not_reachable_nta():
    file_path = "tests/path_not_realizable"
    return list_nta_in_dir(file_path)

def path_exists():
    file_path = "tests/path_exists"
    return list_nta_in_dir(file_path)

def path_not_exists():
    file_path = "tests/path_not_exists"
    return list_nta_in_dir(file_path)

def generator_ntas():
    file_path = "examples/generator"
    return list_nta_in_dir(file_path)

def epsilon_tests():
    file_path = "tests/epsilon_tests"
    return list_nta_in_dir(file_path)

def read_file(fp):
    return uppaalpy.core.NTA.from_xml(fp)

def write_to_file(nta):
    return nta.to_file('/tmp/out.xml')

def write_to_file_pretty(nta):
    return nta.to_file('/tmp/out.xml', pretty=True)

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



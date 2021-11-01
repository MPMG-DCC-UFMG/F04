import copy
import json
import os
import sys


def get_full_path(folder):
    answer = ''
    if folder.startswith('/'):
        answer = copy.deepcopy(folder)
    else:
        answer = os.getcwd() + '/' + folder

    while answer and answer.endswith('/'):
        answer = answer[:-1]

    return answer


def assert_folder_exists(full_path):
    if not full_path.startswith('/'):
        return

    elements = [ w for w in full_path.split('/') if w.strip() ]

    current_folder = ''
    for w in elements:
        current_folder += '/' + w
        if not os.path.isdir(current_folder):
            os.mkdir(current_folder)


    return


if __name__ == '__main__':
    jason = None
    is_portuguese = False
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if os.path.isfile(filename):
            with open(filename, 'rt') as fr:
                try:
                    jason = json.load(fr)
                except Exception as e:
                    jason = { 'erro': 'problem loading "%s": %s' % (filename, str(e)) }

            if 'pasta_da_saida' in jason:
                is_portuguese = True
                jason['output'] = copy.deepcopy(jason['pasta_da_saida'])

            jason['output'] = get_full_path(jason['output']) if 'output' in jason else get_full_path('data')

            try:
                assert_folder_exists(jason['output'])
            except Exception as e:
                folder = copy.deepcopy(jason['output'])
                jason = { 'erro': 'problem creating "%s" folder: %s' % (folder, str(e)) }
        else:
            jason = { 'erro': 'file "%s" not found' % filename }
    else:
        jason = { 'erro': 'filename must be passed as argument'}

    if '--output-folder' in sys.argv:
        print(jason['output'] if 'output' in jason else '/')
    else:
        if is_portuguese:
            jason['pasta_da_saida'] = copy.deepcopy(jason['output'])
            del jason['output']
        print(json.dumps(jason))

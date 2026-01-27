import time
import zipfile
from os import mkdir, walk, makedirs
from shutil import copy as fcopy, copytree, rmtree, make_archive
from os.path import exists, dirname, join

file_dir = dirname(__file__)
relase_path = join(file_dir, 'release')
if not exists(relase_path):
    mkdir(relase_path)

file_dir = join(file_dir, 'dist', 'ArcSvgTool')

def time2str(t):
    return time.strftime(r'%Y%m%d_%H%M%S', time.localtime(t))

file_name = 'ArcSvgTool'
export_file_name = '{}_{}'.format(file_name, time2str(time.time()))
export_archive_path = join(relase_path, export_file_name)
print(export_archive_path)

paths = []
filter_names = [
    '__pycache__',
    'temp',
    'logs',
    'release',
    'output'
]
filter_file_names = [
    'config.json'
]
for root, dirs, files in walk(file_dir):
    if root == file_dir:
        _files = []
        for _file in files:
            if _file not in filter_file_names:
                _files.append(_file)
        paths.append((root, _files))
        continue
    root_splits = root.split('\\')[::-1]
    flag = False
    for r in root_splits:
        if r in filter_names:
            flag = True
            break
    if flag:
        continue
    paths.append((root, files))

temp_folder_path = join(file_dir, 'temp')
if not exists(temp_folder_path):
    mkdir(temp_folder_path)

for path in paths:
    dir_path = path[0]
    files = path[1]

    folder_name = (dir_path.replace(file_dir, ''))
    tmp_path = temp_folder_path + '/' + folder_name
    if not exists(tmp_path):
        makedirs(tmp_path)

    for _file in files:
        src_file_path = join(dir_path, _file)
        dst_file_path = join(tmp_path, _file)
        fcopy(src_file_path, dst_file_path)

make_archive(export_archive_path, 'zip', temp_folder_path)

rmtree(temp_folder_path)

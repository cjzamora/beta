# -*- coding: utf-8 -*-

import os
import sys
import urllib
import urlparse
import hashlib
import shutil
import subprocess
import simplejson as json
import numpy as np

# get root path
ROOT_PATH = os.path.abspath(os.getcwd())

# log colors
LOG_COLORS = {
    'default' : '\033[37m%s \033[0m',
    'success' : '\033[32m%s \033[0m',
    'warning' : '\033[33m%s \033[0m',
    'error'   : '\033[31m%s \033[0m',
    'system'  : '\033[35m%s \033[0m'
}

# get root path
def get_root():
    return ROOT_PATH

# get configuration file
def get_config():
    path = os.path.join(ROOT_PATH, 'conf', 'settings.json')

    return read_file(path, True)

# get paths
def get_path(path=None):
    if path != None:
        return os.path.join(ROOT_PATH, get_config()['paths'][path])

    paths    = get_config()['paths']
    absolute = {}

    for i in paths:
        absolute[i] = os.path.join(ROOT_PATH, paths[i])

    return absolute

# get commands
def get_command(path=None):
    if path != None:
        return get_config()['commands'][path]

    return get_config()['commands']

# url parser
def parse_url(site):
    return urlparse.urlparse(site)

# generate has
def generate_hash(hash):
    return hashlib.md5(hash).hexdigest()

# read file from path
def read_file(path, asJson=False):
    with open(path) as file:
        data = file.read()

        if asJson == True:
            return json.loads(data)

        return data

# write file from path
def write_file(path, data, isJson=False):
    # open file for writing
    with open(path, 'w+') as f:
        if isJson == True:
            f.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf8'))

            return True

        f.write(data)

        return True

# check if file exists
def file_exists(path):
    if not os.path.exists(path):
        return False

    return True

# clear folder
def clear_folder(path):
    # get the folder path
    folder = path

    # iterate on each path in the given folder
    for file in os.listdir(folder):
        # get the file path
        file_path = os.path.join(folder, file)

        try:
            # is it a file?
            if os.path.isfile(file_path):
                # remove it
                os.unlink(file_path)
        except Exception as e:
            print(e)

# load training data
def load_training():
    # get training path
    path = get_path('training')

    # training files
    files = []

    # iterate on training folder
    for file in os.listdir(path):
        # get all json training data
        if file.endswith('json'):
            # append the file
            files.append(os.path.join(path, file))

    # training data's
    training = []

    # iterate on each file and read it
    for i in files:
        data = json.loads(open(i).read())

        # skip empty data
        if data == None:
            continue

        # iterate on each data
        for k in data:
            # append to training data
            training.append(k)

    return training

# process url
def process_url(url):
    id = generate_hash(
         parse_url(url).path + 
         parse_url(url).query)

    return {
        'site_name' : parse_url(url).netloc,
        'site_id'   : id
    }

# makedir
def make_dir(path):
    # path exists?
    if not os.path.exists(path):
        # create directory
        os.makedirs(path)

# pretty print object
def pretty(object):
    print json.dumps(object, indent=2).encode('utf8')

# log colors
def log(message, type='default', newlines=0):
    print LOG_COLORS[type] % message

    for i in range(0, newlines):
        print '\n'
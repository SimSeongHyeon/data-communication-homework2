import json
import numpy as np
from ast import literal_eval

def dict_to_str(dictionary):
    return json.dumps(dictionary)

def str_to_dict(string):
    return json.loads(string)

def matrix_to_dict(matrix):
    return {"matrix": matrix.tolist()}

def dict_to_matrix(dictionary):
    return np.array(dictionary["matrix"])
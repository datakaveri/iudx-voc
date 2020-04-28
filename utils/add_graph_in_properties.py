#!/usr/local/bin/python3

import json
import os,glob
import copy

folder_path = "../base-schemas/properties/"
for filename in glob.glob(os.path.join(folder_path, '*.jsonld')):
    with open(filename, "r+") as obj_file:
        new_dict ={}
        new_list = []
        obj = json.load(obj_file)
        template = copy.deepcopy(obj)
        del(obj["@context"]) 
        new_list.append(copy.deepcopy(obj))
        new_dict["@graph"] = new_list
        new_dict["@context"] = template["@context"]
        
        obj_file.seek(0)
        json.dump(new_dict, obj_file, indent=4)
        obj_file.truncate()
#!/usr/local/bin/python3
import json
import os
import glob
import copy
import sys


folder_path = sys.argv[1]
#folder_path = "../../base-schemas/classes_expanded/"

with open("./iudx-voc-properties.txt", "w+") as text_file:
    

    def graph(obj):
        if "@graph" in obj.keys():
            graph_obj = copy.deepcopy(obj["@graph"])
            for i in obj["@graph"]:
                if isinstance(i["@type"], list):
                    typ = i["@type"][0].split(":")
                    if typ[1] == "Class":
                        class_name = i["@id"].replace(":", "_")
                        print("class " + class_name + "{", file=text_file) 
                        for j in graph_obj:
                            if "Property" in j["@type"]:
                                print("\t" + j["@id"].replace(":", "_"), file=text_file)
                        print("}", file=text_file)
                        try:
                            superclass_name = i["rdfs:subClassOf"]["@id"].replace(":", "_")
                            super_class = i["rdfs:subClassOf"]["@id"]
                            if "rdf:" not in super_class:
                                super_class = super_class.split(":")
                                with open(folder_path + super_class[1] + ".jsonld", "r+") as super_file:
                                    super_obj = json.load(super_file)
                                    graph(super_obj)
                            print(superclass_name + " --|> " + class_name + " : SubClass", file=text_file)
                        except KeyError:
                            pass
                elif "Class" in i["@type"]:
                    typ = i["@type"].split(":")
                    if typ[1] == "Class":
                        class_name = i["@id"].replace(":", "_")
                        print("class " + class_name + "{", file=text_file) 
                        for j in graph_obj:
                            if "Property" in j["@type"]:
                                print("\t" + j["@id"].replace(":", "_"), file=text_file)
                        print("}", file=text_file)
                        try:
                            superclass_name = i["rdfs:subClassOf"]["@id"].replace(":", "_")
                            super_class = i["rdfs:subClassOf"]["@id"]
                            if "rdf:" not in super_class:
                                super_class = super_class.split(":")
                                with open(folder_path + super_class[1] + ".jsonld", "r+") as super_file:
                                    super_obj = json.load(super_file)
                                    graph(super_obj)
                            print(superclass_name + " --|> " + class_name + " : SubClass", file=text_file)
                        except KeyError:
                            pass
        else:
            print("@graph missing in " + filename)
    
    filename = "../../bs-dm/classes_expanded/Resource.jsonld"
    #for filename in glob.glob(os.path.join(folder_path, '*.jsonld')):
    with open(filename, "r+") as obj_file:
         obj = json.load(obj_file)
         print(filename.replace(sys.argv[1], ""), file=text_file)
         #print(filename.replace("../../base-schemas/classes_expanded", ""))
         graph(obj)
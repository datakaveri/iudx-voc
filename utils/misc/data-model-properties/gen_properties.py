#! /usr/local/bin/python3

import csv
import json
import copy
import os
from collections import OrderedDict


csv_file_path = [
#                "./Device - Device_properties.csv"]
#                "./Environment - EnvAQM_new_properties.csv", "./Environment - EnvFlood_properties.csv" ]
#                "./Environment - EnvAQM_new_properties.csv", "./Environment - EnvFlood_properties.csv", "./Environment - EnvWeather_properties.csv"]
              "./WasteManagement - WasteManagementBin.csv", "./WasteManagement - WasteManagementVehicle.csv"
              ]
""" Add the property names to ignore list to skip property generation. """
#ignore = ["Custom", "location", "deviceModel", "rainfallMeasured", "rainfallForecast", "name", ""]

if not os.path.exists("./Properties/"):
    os.makedirs("./Properties/")
properties_path = "./Properties/"


with open("./template.jsonld", "r") as template:
    obj = json.load(template)


def check_multiple_includes(includes):
    if "," in includes:
        includes_list = includes.split(",")
    else:
        includes_list = []
        includes_list.append(includes)
    return includes_list


def which_iudx_property(prop_type):
    if prop_type == "QP":
        prop_list = []
        prop_list.append("iudx:QuantitativeProperty")
        return prop_list
    elif prop_type == "TP":
        prop_list = []
        prop_list.append("iudx:TimeProperty")
        return prop_list
    elif prop_type == "TXP":
        prop_list = []
        prop_list.append("iudx:TextProperty")
        return prop_list
    elif prop_type == "SP":
        prop_list = []
        prop_list.append("iudx:StructuredProperty")
        return prop_list
    elif prop_type == "GP":
        prop_list = []
        prop_list.append("iudx:GeoProperty")
        return prop_list


def add_domain_or_range(domain_range_list, domain_range):
    try:
        dr_list = []
        for item in domain_range_list:
            dr_dict = {}
            if ":" in item:
                dr_dict["@id"] = item.strip()
            else:
                dr_dict["@id"] = "iudx:" + item.strip()
            dr_list.append(dr_dict)
    except NameError:
        dr_list = []
        dr_dict = {}
        if ":" in domain_range:
            dr_dict["@id"] = domain_range.strip()
        else:
            dr_dict["@id"] = "iudx:" + domain_range.strip()
        dr_list.append(dr_dict)
    return dr_list


def add_similar_match(match):
    match_dict = {}
    match_dict["@id"] = match
    return match_dict


def order_obj(obj):
    new_dict = OrderedDict()
    if "@context" in obj.keys():
        new_dict["@context"] = obj["@context"]
        del(obj["@context"]) 
    if "@graph" in obj.keys():
        new_list = []
        tmp_obj = OrderedDict()
        new_list.append(tmp_obj)
        try:
            tmp_obj["@id"] = obj["@graph"][0]["@id"]
        except KeyError:
            pass
        try:
            tmp_obj["@type"] = obj["@graph"][0]["@type"]
        except KeyError:
            pass
        try:
            tmp_obj["rdfs:comment"] = obj["@graph"][0]["rdfs:comment"]
        except KeyError:
            pass
        try:
            tmp_obj["rdfs:label"] = obj["@graph"][0]["rdfs:label"]
        except KeyError:
            pass
        try:
            tmp_obj["iudx:domainIncludes"] = obj["@graph"][0]["iudx:domainIncludes"]
        except KeyError:
            pass
        try:
            tmp_obj["iudx:rangeIncludes"] = obj["@graph"][0]["iudx:rangeIncludes"]
        except KeyError:
            pass
        try:
            del(obj["@graph"][0]["@id"])
        except KeyError:
            pass
        try:
            del(obj["@graph"][0]["@type"])
        except KeyError:
            pass
        try:
            del(obj["@graph"][0]["rdfs:comment"])
        except KeyError:
            pass
        try:
            del(obj["@graph"][0]["rdfs:label"])
        except KeyError:
            pass
        try:
            del(obj["@graph"][0]["iudx:domainIncludes"])
        except KeyError:
            pass
        try:
            del(obj["@graph"][0]["iudx:rangeIncludes"])
        except KeyError:
            pass
        new_dict["@graph"] = new_list
        if bool(obj):
            new_dict["@graph"][0].update(obj["@graph"][0])
        return new_dict


def gen_properties(file_path):
    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        data = data[1:]
        for item in data:
            if item[7] == "0":
                new_dict = OrderedDict()
                new_dict["@context"] = obj["@context"]
                csv_label = item[0].strip()
                csv_type = item[1].strip()
                csv_comment = item[2].strip()
                csv_domain = item[3].strip()
                csv_range = item[4].strip()
                csv_match = item[5].strip()
                csv_domain_list = check_multiple_includes(csv_domain)
                csv_range_list = check_multiple_includes(csv_range)
                if "@graph" in obj.keys():
                    new_list = []
                    tmp_obj = OrderedDict()
                    new_list.append(tmp_obj)
                    tmp_obj["@id"] = "iudx:" + csv_label
                    tmp_obj["@type"] = which_iudx_property(csv_type)
                    tmp_obj["rdfs:comment"] = csv_comment
                    tmp_obj["rdfs:label"] = csv_label
                    tmp_obj["rdfs:isDefinedBy"] = obj["@graph"][0]["rdfs:isDefinedBy"]
                    tmp_obj["iudx:domainIncludes"] = add_domain_or_range(csv_domain_list, csv_domain)
                    tmp_obj["iudx:rangeIncludes"] = add_domain_or_range(csv_range_list, csv_range)
                    if csv_match:
                        tmp_obj["skos:exactMatch"] = add_similar_match(csv_match)
                    new_dict["@graph"] = new_list
                    with open(properties_path + csv_label + ".jsonld", "w+") as prop_file:
                        json.dump(new_dict, prop_file, indent=4)
                else:
                    print("@graph missing in  "+ csv_label)
            if item[8] == "1":
                base_property = item[0]
                new_domain = item[3]
                with open("../../../base-schemas/properties/"+base_property+".jsonld","r+") as base_file:
                    base_prop = json.load(base_file)
                    new_domain_obj = {"@id": "iudx:"+new_domain}
                    if new_domain_obj not in base_prop["@graph"][0]["iudx:domainIncludes"]:
                        base_prop["@graph"][0]["iudx:domainIncludes"].append(new_domain_obj)
                    ordered_prop = order_obj(base_prop)
                    base_file.seek(0)
                    json.dump(ordered_prop, base_file, indent=4)
                    base_file.truncate()


if __name__=="__main__":
    for path in csv_file_path:
        gen_properties(path)

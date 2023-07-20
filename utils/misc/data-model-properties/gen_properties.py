import deepdiff
# deepdiff 5.8.1

import csv
import json
import copy
import os
from collections import OrderedDict
import pandas as pd
import os, fnmatch
from pathlib import Path
import os.path as path
from tkinter import Tk
from tkinter import filedialog

# tk 8.6
""" Add the property names to ignore list to skip property generation. """
# ignore = ["Custom", "location", "deviceModel", "rainfallMeasured", "rainfallForecast", "name", ""]

Tk().withdraw()
file_dir = filedialog.askopenfilename(title="Select A File")
dir_home = path.abspath(path.join(os.path.abspath(file_dir), "../../../.."))

with open(dir_home + "/utils/misc/data-model-properties/template.jsonld", "r") as template:
    obj = json.load(template)


def check_dir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def write_json(base_prop, base_file):
    ordered_prop = order_obj(base_prop)
    base_file.seek(0)
    json.dump(ordered_prop, base_file, indent=4)
    base_file.truncate()


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


def add_domain_or_range(item_list, items, item_type):
    try:
        dr_list = []
        for item in item_list:
            dr_dict = {}
            if ":" in item:
                dr_dict["@id"] = item.strip()
            else:
                if item.strip() == "Text-list":
                    dr_dict["@container"] = "@list"
                    dr_dict["@id"] = "iudx:Text"
                else:
                    dr_dict[
                        "@id"] = "iudx:" + item.strip().capitalize() if item_type == "iudx:rangeIncludes" and item.strip() not in [
                        "NumericArray", "ValueDescriptor"] else "iudx:" + item.strip()
            dr_list.append(dr_dict)
            for i in range(len(dr_list)):
                if "@container" in dr_list[i].keys():
                    if {'@id': 'iudx:Text'} in dr_list:
                        dr_list.remove({'@id': 'iudx:Text'})
    except NameError:
        dr_list = []
        dr_dict = {}
        if ":" in items:
            dr_dict["@id"] = items.strip()
        else:

            dr_dict[
                "@id"] = "iudx:" + items.strip().capitalize() if item_type == "iudx:rangeIncludes" else "iudx:" + items.strip()
        dr_list.append(dr_dict)
    return dr_list


def add_similar_match(match):
    match_dict = {}
    match_dict["@id"] = match
    return match_dict


def find_name(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def create_classes(properties_path):
    subdomain_path = properties_path + "/" + sub_domain + ".jsonld"
    if not os.path.exists(subdomain_path):
        comment = input("Enter the description for the sub domain\n")
        class_dict = obj
        del class_dict["@context"]['skos']
        del class_dict["@context"]['schema']
        del class_dict["@context"]['geojson']
        del class_dict["@context"]['xsd']
        class_dict["@graph"][0]["@type"] = ["owl:Class", "rdfs:Class"]
        class_dict["@graph"][0]["@id"] = "iudx:" + sub_domain
        class_dict["@graph"][0]["rdfs:comment"] = comment
        class_dict["@graph"][0]["rdfs:label"] = sub_domain
        dict1 = {}
        dict1["rdfs:subClassOf"] = {"@id": "iudx:" + domain_name}
        obj["@graph"][0].update(dict1)

        with open(subdomain_path, "w+") as prop_file:
            json.dump(class_dict, prop_file, indent=4)


def order_obj(obj):
    new_dict = OrderedDict()
    if "@context" in obj.keys():
        new_dict["@context"] = obj["@context"]
        del (obj["@context"])
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
            del (obj["@graph"][0]["@id"])
        except KeyError:
            pass
        try:
            del (obj["@graph"][0]["@type"])
        except KeyError:
            pass
        try:
            del (obj["@graph"][0]["rdfs:comment"])
        except KeyError:
            pass
        try:
            del (obj["@graph"][0]["rdfs:label"])
        except KeyError:
            pass
        try:
            del (obj["@graph"][0]["iudx:domainIncludes"])
        except KeyError:
            pass
        try:
            del (obj["@graph"][0]["iudx:rangeIncludes"])
        except KeyError:
            pass
        new_dict["@graph"] = new_list
        if bool(obj):
            new_dict["@graph"][0].update(obj["@graph"][0])
        return new_dict


def jsonld_update(filename, domain, column_name, schema):
    with open(filename, "r+") as base_file:

        base_prop = json.load(base_file)
        domains_list = domain.split(",")
        domains_list = list(filter(str.strip, domains_list))

        dn_new_list = add_domain_or_range(domains_list, domain, column_name)
        dn_existing = base_prop["@graph"][0][column_name]

        if dn_new_list != dn_existing:
            for new_domain in dn_new_list:
                if new_domain not in dn_existing:
                    if schema == "baseSchema":
                        print("Base Schema Property file : ", os.path.basename(filename) + " updated with ->",
                              new_domain)
                    else:
                        print("Other Schema Property file : ", os.path.basename(filename) + " updated with ->",
                              new_domain)

                    dn_existing.append(new_domain)

            base_prop["@graph"][0][column_name] = dn_existing
            ordered_prop = order_obj(base_prop)
            base_file.seek(0)
            json.dump(ordered_prop, base_file, indent=4)
            base_file.truncate()


def gen_properties(df):
    for index, item in df.iterrows():
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
            properties_path = model_name_dir + "/properties/" + csv_label + ".jsonld"

            if "@graph" in obj.keys():
                new_list = []
                tmp_obj = OrderedDict()
                new_list.append(tmp_obj)
                tmp_obj["@id"] = "iudx:" + csv_label
                tmp_obj["@type"] = which_iudx_property(csv_type)
                tmp_obj["rdfs:comment"] = csv_comment
                tmp_obj["rdfs:label"] = csv_label
                tmp_obj["rdfs:isDefinedBy"] = obj["@graph"][0]["rdfs:isDefinedBy"]
                tmp_obj["iudx:domainIncludes"] = add_domain_or_range(csv_domain_list, csv_domain, "iudx:domainIncludes")
                tmp_obj["iudx:rangeIncludes"] = add_domain_or_range(csv_range_list, csv_range, "iudx:rangeIncludes")
                if csv_match != 'nan':
                    tmp_obj["skos:exactMatch"] = {'@id': csv_match}
                new_dict["@graph"] = new_list

                check_dir(model_name_dir + "/properties")

                if os.path.exists(properties_path):
                    with open(properties_path, "r+") as base_file:
                        base_prop = json.load(base_file)
                        diff = deepdiff.DeepDiff(base_prop, json.loads(json.dumps(new_dict)))
                        if diff:
                            if list(diff.keys()).count("values_changed"):
                                print("Existing Property: ", csv_label, " - Value Changes -> ",
                                      [k.split("root['@graph'][0]")[1] for k, v in diff["values_changed"].items()])
                            if list(diff.keys()).count("iterable_item_added"):
                                print("Existing Property: ", csv_label, " - Value Additions -> ",
                                      [k.split("root['@graph'][0]")[1] for k, v in diff["iterable_item_added"].items()])
                            if csv_match != 'nan':
                                base_prop["@graph"][0]["skos:exactMatch"] = {'@id': csv_match}

                            base_prop["@graph"][0]["@type"] = which_iudx_property(csv_type)
                            base_prop["@graph"][0]["rdfs:comment"] = csv_comment
                            base_prop["@graph"][0]["iudx:rangeIncludes"] = add_domain_or_range(csv_range_list,
                                                                                               csv_range,
                                                                                               "iudx:rangeIncludes")

                            csv_domain = csv_domain.split(",")
                            for i in range(len(csv_domain)):
                                new_domain = csv_domain[i].strip()
                                new_domain_obj = {"@id": "iudx:" + new_domain}
                                if new_domain_obj not in base_prop["@graph"][0]["iudx:domainIncludes"]:
                                    base_prop["@graph"][0]["iudx:domainIncludes"].append(new_domain_obj)
                            write_json(base_prop, base_file)

                if not os.path.exists(properties_path):
                    with open(properties_path, "w+") as prop_file:
                        json.dump(new_dict, prop_file, indent=4)
                        print("New Property added - ", csv_label + ".jsonld")

            else:
                print("@graph missing in  " + csv_label)
        if item[8] == "1":
            base_property = item[0]
            domain = item[3]
            range_include = item[4].strip()
            filename = dir_home + "/base-schemas/properties/" + base_property + ".jsonld"
            jsonld_update(filename, domain, "iudx:domainIncludes", "baseSchema")
            jsonld_update(filename, range_include, "iudx:rangeIncludes", "baseSchema")

        if item[7] == "1":
            # try:
            base_property = item[0]
            domain = item[3]
            range_include = item[4].strip()
            property_path = find_name(base_property + '.jsonld', dir_home)
            jsonld_update(property_path[0], domain, "iudx:domainIncludes", "")
            jsonld_update(property_path[0], range_include, "iudx:rangeIncludes", "")

        # except:
        #    print(f"NOT FOUND in Other Schema: {base_property}  ")


if __name__ == "__main__":

    domain_name = input("Enter the Domain name (without trailing or inline spaces)\n")
    val = input("Do you want to add a new Domain (Y/N)\n").upper()
    if val == "Y":
        arr = next(os.walk(dir_home + "/data-models"))
        if domain_name in arr[1]:
            print("Domain already exists")

    sub_domain = Path(file_dir).stem

    model_name_dir = dir_home + "/data-models/" + domain_name

    check_dir(model_name_dir)

    class_path = model_name_dir + "/classes"
    check_dir(class_path)
    create_classes(class_path)

    # for i in range(len((pd.ExcelFile(file_dir)).sheet_names)):
    #     df = pd.read_excel(file_dir, sheet_name=i).astype(str)
    #     gen_properties(df)
    df = pd.read_csv(file_dir).astype(str)
    gen_properties(df)
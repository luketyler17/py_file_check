import sys, argparse, os, json
import yaml
import os

__all__ = ['get_path']

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--ifile", help="JSON file to be analyzed", required=True)
argParser.add_argument("-y", "--yaml", help="YAML Config file that contains keywords to be searched", required=True)
argParser.add_argument("-d", "--directory", help="Directory to place JSON files in, by default will use current working directory, will create directory if directory passed does not exist")
argParser.add_argument("-clean", "--clean", action='store', nargs='*', help="Cleans directory of previous files created by this program")

def main(args) -> None:
    if not args.directory:
        # make current working directory the output directory if no directory was provided
        directory = os.getcwd()
        args.directory = os.path.join(directory, "py_filter_output")
        print(f"\nOutputting all found matches into: {args.directory}")
    if not os.path.exists(args.directory):
        # creates directory if it doesn't exist
        os.makedirs(args.directory)

    output_found_file = os.path.join(args.directory, "py_filter_found.json")
    output_not_found_file = os.path.join(args.directory, "not_found.json")

    if args.clean is not None:
        # clean was called, remove the files this script creates within the directory
        os.remove(output_found_file)
        os.remove(output_not_found_file)
        print(f"\nCleaning py_filter files found in {args.directory}")
    with open(args.yaml) as f:
        # open yaml file for filters
        yaml_data = yaml.safe_load(f)

    with open(args.ifile) as input_file:
        # open json file and iterate through all json objects
        data = json.load(input_file)
        i = 0

        found_dictionary = []
        unfound_dictionary = []
        while(i < len(data)):
            x = get_path(data[i], yaml_data['filters'])
            if x:
                # value was found in dictionary, path and value are held within x, i is the index of the dict w/found values
                found_dictionary.append(data[i])
            else:
                # no value was found in dict, write data to unfound_file
                unfound_dictionary.append(data[i])
            i += 1

        # If overwriting the same file is fine, use this block
        # with open(output_found_file, "w+") as outFile:
        #     #appends file if exists inside of target directory
        #     json.dump(found_dictionary, outFile, indent=6)
        #     outFile.close()
        # with open(output_not_found_file, "w+") as outFile:
        #     json.dump(unfound_dictionary, outFile, indent=6)
        #     outFile.close()
        # input_file.close()

        # if needed to append instead of overwriting, have to pull the JSON out, append to the dictionary then add it back to the file
        try:
            #have to load the original file in order to write valid JSON
            with open(output_found_file) as origin:
                data = json.load(origin)
                #adding arrays of dicts together for valid JSON output
                data = data + found_dictionary
                origin.close()
        #if the file does not exist, its not an err, just first time ran/files were cleared
        except FileNotFoundError as err:
            data = found_dictionary
        with open(output_found_file, "w+") as outFile:
            print("Writing Found Matches")
            json.dump(data, outFile, indent=6)
            data = None
            outFile.close()
        try:
            #have to load the original file in order to write valid JSON
            with open(output_not_found_file) as origin:
                data = json.load(origin)
                #adding arrays of dicts together for valid JSON output
                data = data + unfound_dictionary
                origin.close()
        #if the file does not exist, its not an err, just first time ran/files were cleared
        except FileNotFoundError as err:
            data = unfound_dictionary
        with open(output_not_found_file, "w+") as outFile:
            print("writing unmatched data")
            json.dump(data, outFile, indent=6)
            data = None
            outFile.close()
        
        print(f"py_filter finished, found files are in {args.directory}\n{output_found_file} contains json of matches\n{output_not_found_file} contains json with no values found\n")


def get_path(dict_input, filter_values, prepath=""):
    __doc__ = '''Recursive function that will span all trees in json file to find specific values passed in. Takes 2 arguments to start, a dictionary input & list of values, 
                 prepath is used for the indexing of the item found. This function returns a list - x[0] is the path to the object, x[1] is the filter keyword found'''
    '''
    Function takes in three values - a dictionary, the values to search for, in a list, and a prepath that is set to default to an empty string.
    Function recursively looks through dictionary for first hit of any value in the value list, when found will return a list with the path in x[0] and the value found in x[1]
    In the main() function -> this will write out the 
    '''
    if type(dict_input) is not dict:
            if type(dict_input) is dict or type(dict_input) is list:
                for index, value in enumerate(dict_input):
                    path = prepath + f"[{index}]"
                    x = get_path(value, filter_values, path)
                    if x:
                        return x
            else:
                if dict_input in filter_values:
                    path = prepath + f"[{index}]"
                    return [path, value]
                         
    else:
        for key, v in dict_input.items():
            path = prepath + f".{key}"
            if v in filter_values:
                return [path, v]
            elif type(v) is dict or type(v) is list:
                if type(v) is list:
                    #have to check if each value in list is not another nested list or dict, enumerate over the objects send lists and dicts through recursively
                    for index, value in enumerate(v):
                        new_path = path + f"[{index}]"
                        if type(value) is list:
                            #type is list, check every value to ensure no value lower is also a list/dict
                            i = 0
                            new_val = v[index]
                            while i < len(new_val):
                                third_path = new_path + f"[{i}]"
                                x = get_path(new_val[i], filter_values, third_path)
                                if x:
                                    return x
                                i += 1
                        elif type(value) is dict:
                            #have a nested dictionary, take the found dict value and submit back through get_path
                            x = get_path(value, filter_values, new_path)
                            if x:
                                return x
                        else:
                            #know type is list with no nested dicts -> search through list return the path and the item found
                            if value in filter_values:
                                return [new_path, value]
                else:
                    #is a dictionary, access the values by passing dict back into function
                    x = get_path(v, filter_values, path)
                    if x:
                        return x


if __name__ == "__main__":
    args = argParser.parse_args()
    main(args)

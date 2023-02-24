import json
import unittest

import yaml
import os
import csv
import logging
from py_filter import get_path

logging.basicConfig(filename="file_check.log",
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S')


def csv_checker(search_values: list, data_to_search, path: str) -> None:
    # have to iterate through both lists - item could be in any place at any point in the csv file
    # once found -> break and add to check -> if check == len(search_values) all values were found
    check = 0
    for item in search_values:
        for line in data_to_search:
            if item in line:
                check += 1
                break
    if check != len(search_values):
        logging.error(f"FAIL - search strings {search_values} were not all found within {path}")
    else:
        logging.debug(f"SUCCESS - search strings {search_values} found within {path}")
        print("CSV Values found in dataset")


def json_checker(search_values: list, data_to_search, path: str) -> None:
    check = 0
    for value_to_find in search_values:
        get_path_return = get_path(data_to_search, [value_to_find])
        if get_path_return:
            # get path returned, string was located in json
            # increment check to show that value has returned
            check += 1
    # if check is not equal to the total amount of values within search_values,
    # one of the values is not found within the file
    if check != len(search_values):
        logging.error(f"FAIL - search strings {search_values} were not all found within {path}")
    else:
        logging.debug(f"SUCCESS - search strings {search_values} found within {path}")
        print("JSON Values found in dataset")


def main(input_yaml_file):
    # takes in yaml file, reads to dict
    # attempts to find every file in yaml_file
    # attempts to load dataset of passed files - currently supports: JSON, CSV && TXT
    # checks for each search field over every line of data, when it is found breaks and logs success/fail
    # if not found will log fail

    with open(input_yaml_file, 'r') as yFile:
        stream = yaml.safe_load(yFile)
        for path, search_values in stream.items():
            # attempt to open every file, if file cannot open/cannot be found
            # handle the err and continue
            try:
                check = 0
                with open(path, 'r') as file_to_search:
                    # checking for CSV files
                    if path.lower().endswith('.csv'):
                        csv_values = csv.reader(file_to_search)
                        csv_checker(search_values, csv_values, path)

                    # checking for JSON Files
                    elif path.lower().endswith('.json'):
                        try:
                            json_values = json.loads(file_to_search.read())
                            json_checker(search_values, json_values, path)

                        except json.JSONDecodeError:
                            logging.error(f"FAIL - file {path} was unable to be decoded as json")

                    # assumed to be a txt file after
                    else:
                        for value in search_values:
                            # reset file to beginning for search
                            file_to_search.seek(0)
                            for line in file_to_search:
                                if value in line:
                                    check += 1
                                    break
                        if check != len(search_values):
                            logging.error(f"FAIL - search strings {search_values} were not all found within {path}")
                        else:
                            logging.debug(f"SUCCESS - search strings {search_values} found within {path}")
                            print("Values found in txt dataset")

            except FileNotFoundError as err:
                logging.error(f"File {path} was not found")


class FileCheckTest(unittest.TestCase):
    def test_pass_text_file(self):
        main("test_files/pass_test_txt.yaml")
        self.assertTrue(os.path.isfile("file_check.log"))
        check_file = open("file_check.log", "r+")
        self.assertTrue("SUCCESS - search strings ['hello', 'world', 'luke'] found within " in check_file.readline())
        check_file.truncate(0)
        check_file.close()

    def test_fail_text_file(self):
        main("test_files/fail_test_txt.yaml")
        self.assertTrue(os.path.isfile("file_check.log"))
        check_file = open("file_check.log", "r+")
        self.assertTrue("FAIL - search strings ['do', 'not', 'work']" in check_file.readline())
        check_file.truncate(0)
        check_file.close()

    def test_pass_csv_checker(self):
        main("test_files/pass_test_csv.yaml")
        self.assertTrue(os.path.isfile("file_check.log"))
        check_file = open("file_check.log", "r+")
        self.assertTrue("SUCCESS - search strings ['An Apple Iphone'] found within" in check_file.readline())
        check_file.truncate(0)
        check_file.close()

    def test_fail_csv_checker(self):
        main("test_files/fail_test_csv.yaml")
        self.assertTrue(os.path.isfile("file_check.log"))
        check_file = open("file_check.log", "r+")
        self.assertTrue("FAIL - search strings ['Luke Bay Tyler']" in check_file.readline())
        check_file.truncate(0)
        check_file.close()

    def test_pass_json_checker(self):
        main("test_files/pass_test_json.yaml")
        self.assertTrue(os.path.isfile("file_check.log"))
        check_file = open("file_check.log", 'r+')
        self.assertTrue("SUCCESS - search strings ['Maisey, Eran'] found within" in check_file.readline())
        check_file.truncate(0)
        check_file.close()

    def test_fail_json_checker(self):
        main("test_files/fail_test_json.yaml")
        self.assertTrue(os.path.isfile("file_check.log"))
        check_file = open("file_check.log", 'r+')
        self.assertTrue("FAIL - search strings ['Luke Bay Tyler']" in check_file.readline())
        check_file.truncate(0)
        check_file.close()


if __name__ == '__main__':
    input_file = "paths.yaml"
    unittest.main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

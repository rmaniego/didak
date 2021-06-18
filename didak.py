"""
    (c) 2020 Rodney Maniego Jr.
    Test runner
    MIT License
"""

VERSION = "1.0.0"

print(f"\nDidak v{VERSION}")

print("\nLoading requirements...")
print("Please wait...")

import os
import sys
import zipfile
import argparse
import subprocess

from arkivist import Arkivist
from maguro import Maguro

print("Done.")

def didak(directory, testcase, identifier, sensitive=0, unzip=0, reset=0):
    
    if not isinstance(directory, str):
        print("\nDidakError: 'directory' parameter must be a string.")
        return
    
    directory = directory.replace("\\", "/")
    if directory[-1] == "/":
        directory = directory[:-1]
    
    if not isinstance(identifier, str):
        print("\nDidakError: 'identifier' parameter must be a string.")
        return

    sensitive = validate(sensitive, 0, 1, 0)
    unzip = validate(unzip, 0, 1, 0)
    reset = validate(reset, 0, 1, 0)
    
    testcase_filename = ""
    if isinstance(testcase, str):
        if not check_path(testcase):
            print("\nDidakWarning: Test case file was not found.")
            testcase = None
    
    testcase = testcase.replace("\\", "/")
    
    
    if not check_path(f"{directory}/didak"):
        os.makedirs(f"{directory}/didak")
    
    if unzip == 1:
        print("\nUnzipping files:")
        for filename in get_filenames(directory, "zip"):
            print(f" - {filename}")
            extract(f"{directory}/{filename}", f"{directory}")

    print("\nAnalyzing files...")
    
    prev = ""
    testcase_filename = testcase.split("/")[-1:][0]

    analysis = Arkivist(f"{directory}/didak/analysis.json", sort=True)
    if reset == 1:
        analysis.clear()
    filenames = get_filenames(f"{directory}", "py")
    for filename in filenames:
        if identifier == "" or identifier in filename:
            metadata = analyze(directory, filename, testcase, sensitive)
            analysis.set(filename, metadata)
    
    print("\nGenerating report...")
    
    count = 0
    analysis.reload()
    for filename, metadata in analysis.items():
        if identifier == "" or identifier in filename:
            count += 1
            score = metadata.get("score", 0)
            print(f"File #{count}: {filename}")
            print(f" - {score}")

def analyze(directory, filename, testcase, sensitive):
    metadata = {}
    formatted = []
    keywords = {}
    results = []
    
    script = ""
    with open(f"{directory}/{filename}", "r", encoding="utf-8") as file:
        try:
            script = file.read()
        except:
            pass
    
    if script != "":
        if sensitive == 1:
            script = script.lower()
        data = Maguro(testcase, delimiter="---")
        try:
            for item in data.unpack()[0].split("\n"):
                if item.strip() != "":
                    if sensitive == 1:
                        item = item.lower()
                    key, value = item.split("=")
                    keywords.update({key.strip(): value.strip()})
            
            items = data.unpack()[1]
            if sensitive == 1:
                items = items.lower()
            
            for item in items.split("\n"):
                group = []
                if item.strip() != "":
                    word = []
                    previous = ""
                    quoted = False
                    for character in item:
                        if character == "\"" and previous != "\\":
                            quoted = (not quoted)
                            continue
                        if not quoted and character == ",":
                            group.append("".join(word))
                            word = []
                            continue
                        previous = character
                        word.append(character)
                    group.append("".join(word))
                results.append(group)
        except Exception as e:
            print(e)
            pass
        used = []
        for line in script.split("\n"):
            line = remove_comments(line)
            if line != "":
                if "input" not in line:
                    formatted.append(line)
                else:
                    for key, value in keywords.items():
                        if key not in used:
                            if key in line:
                                variable = line.split("=")[0].strip()
                                formatted.append(f"{variable} = {value}")
                                used.append(key)
        
        with open(f"{directory}/didak/test.py", "w+", encoding="utf-8") as file:
            file.write("\n".join(formatted))
        
        score = 0
        test_results = get_results(f"{directory}/didak/test.py")
        metadata.update({"results": test_results})
        if sensitive == 1:
            test_results = test_results.lower()
        results = list([x for x in results if len(x) > 0])
        for line in test_results.split("\n"):
            for result in results:
                for variant in result:
                    if variant in line:
                        score += 1
                        break
        metadata.update({"score": score})
    return metadata

def remove_comments(line):
    return line.split("#")[0].strip()

def get_results(filepath):
    try:
        results = subprocess.Popen(f"py \"{filepath}\"", shell=True, stdout=subprocess.PIPE).stdout.read()
        results = str(results, "utf-8", "ignore")
        return results
    except:
        return ""

def validate(value, minimum, maximum, fallback):
    if not isinstance(value, int):
        print("DidakWarning: Parameter must be an integer.")
        value = int(fallback)
    if not (minimum <= value <= maximum):
        print(f"DidakWarning: Parameter must be an integer between {minimum}-{maximum}.")
        value = int(fallback)
    return value

def extract(path, destination):
    try:
        with zipfile.ZipFile(path, "r") as zip:
            zip.extractall(destination)
    except:
        print(f"\nDidakWarning: Error in processing ZIP file: {path}")
        pass


def default(value, minimum, maximum, fallback):
    if value is not None:
        if not (minimum <= value <= maximum):
            return fallback
        return value
    return fallback

# file/folder io
def get_folders(source):
    return [f.name for f in os.scandir(source) if f.is_dir()]

def check_path(path):
    if path.strip() == "":
        return False
    return os.path.exists(path)

def get_filenames(path, extension):
    filenames = []
    for filepath in os.listdir(path):
        if filepath.split(".")[-1].lower() == extension:
            filenames.append(filepath)
    return filenames


################
# didak logic  #
################
parser = argparse.ArgumentParser(prog="didak",
                                 description="Similarity didakr.")
parser.add_argument("-d",
                    "--directory",
                    metavar="directory",
                    type=str,
                    help="Directory of the files.",
                    required=True)

parser.add_argument("-t",
                    "--testcase",
                    metavar="testcase",
                    type=str,
                    help="Filepath of the test case file.",
                    required=True)

parser.add_argument("-u",
                    "--unzip",
                    metavar="unzip",
                    type=int,
                    help="Unzip flag")

parser.add_argument("-i",
                    "--identifier",
                    metavar="identifier",
                    type=str,
                    help="Only run filenames with this unique identifier")

parser.add_argument("-s",
                    "--sensitive",
                    metavar="sensitive",
                    type=int,
                    help="Case-sensitivity")

parser.add_argument("-r",
                    "--reset",
                    metavar="reset",
                    type=int,
                    help="Reset data before analyzing files.")

args = parser.parse_args()

# get submissions directory
directory = args.directory
if not check_path(directory):
    print(f"\nDidakError: The directory was not found: {directory}")
    sys.exit(0)

# get testcase path
testcase = args.testcase
if testcase is not None:
    if not check_path(testcase):
        print(f"\nDidakWarning: File was not found: {testcase}")
        sys.exit(0)

# get identifier
identifier = args.identifier
if identifier is None:
    identifier = ""

# set the case-sensitive flag
sensitive = default(args.sensitive, 0, 1, 0)

# set the unzip flag
unzip = default(args.unzip, 0, 1, 0)

# set the clear data flag
reset = default(args.reset, 0, 1, 0)

didak(directory, testcase=testcase, identifier=identifier, sensitive=sensitive, unzip=unzip, reset=reset)
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
    for filename, metadata in analysis.show().items():
        if identifier == "" or identifier in filename:
            count += 1
            score = metadata.get("score", 0)
            print(f"File #{count}: {filename}")
            total_score = metadata.get("score", 0) / metadata.get("max", 1)
            max_score = 1.0
            common = ""
            for filename2, metadata2 in analysis.show().items():
                if filename != filename2:
                    if common == "":
                        temp = common_string(filename, filename2)
                        if len(temp) >= 10:
                            common = temp
                    if common != "" and common in filename2:
                        total_score += metadata2.get("score", 0) / metadata2.get("max", 1)
                        max_score += 1
            print(f" - Current: {score}, Total: {total_score}/{max_score}")

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
        if sensitive == 0:
            script = script.lower()
        data = Maguro(testcase, delimiter="---")
        try:
            for item in data.unpack()[0].split("\n"):
                if item.strip() != "":
                    if sensitive == 0:
                        item = item.lower()
                    key, value = item.split(" = ")
                    keywords.update({key.strip(): value.strip()})
            items = data.unpack()[1]
            if sensitive == 0:
                items = items.lower()
            results = csv(items)
        except:
            pass
        used = []
        for line in script.split("\n"):
            line = remove_comments(line)
            if line != "":
                if ("input(" not in line):
                    formatted.append(line)
                else:
                    if "=" in line:
                        found = False
                        for key, value in keywords.items():
                            if found:
                                break
                            if key not in used:
                                for search in csv(key)[0]:
                                    if search in line:
                                        variable = line.split("=")[0]
                                        formatted.append(f"{variable} = {value}")
                                        used.append(key)
                                        found = True
                                        break
                        if not found:
                            # workaround only
                            variable = line.split("=")[0]
                            formatted.append(f"{variable} = 1")
                    else:
                        # workaround only
                        formatted.append(line.replace("input(", "print("))
                                    
        
        with open(f"{directory}/didak/test.py", "w+", encoding="utf-8") as file:
            file.write("\n".join(formatted))
        
        score = 0
        test_results = get_results(f"{directory}/didak/test.py")
        metadata.update({"results": test_results})
        if sensitive == 0:
            test_results = test_results.lower()
        results = list([x for x in results if len(x) > 0 and "".join(x) != ""])
        for result in results:
            for variant in result:
                if variant in test_results:
                    score += 1
                    break
        metadata.update({"score": score})
        metadata.update({"max": len(results)})
    return metadata

def csv(data):
    table = []
    for line in data.split("\n"):
        row = []
        if line.strip() != "":
            cell = []
            previous = ""
            quoted = False
            for character in line:
                if character == "\"" and previous != "\\":
                    quoted = (not quoted)
                    continue
                if not quoted and character == ",":
                    row.append("".join(cell))
                    cell = []
                    continue
                if quoted:
                    cell.append(character)
                previous = character
            row.append("".join(cell))
        table.append(row)
    return table

def remove_comments(line):
    double_quotes = line.count("\"") - line.count("\\\"")
    single_quotes = line.count("'") - line.count("\\'")
    
    if double_quotes == 0 and single_quotes == 0:
        return list(line.split("#"))[0]
    
    mod_double_quotes = double_quotes % 2
    mod_single_quotes = single_quotes % 2        
    
    if mod_single_quotes == 0 and single_quotes > 0:
        if "\"\"\"" not in line and "'" in line:
            line = line.replace("\"", "\\\"").replace("'", "\"")
    
    cleaned = []
    previous = ""
    
    quoted = False
    skip = False
    for character in line:
        if not skip:
            if character == "\"" and previous != "\\":
                quoted = (not quoted)
            if not quoted and character == "#":
                skip = True
        if not skip:
            cleaned.append(character)
        previous = character
    return "".join(cleaned)

def get_results(filepath):
    try:
        results = subprocess.Popen(f"py \"{filepath}\"", shell=True, stdout=subprocess.PIPE).stdout.read()
        results = str(results, "utf-8", "ignore")
        return results
    except:
        return ""

def common_string(original, compare, reverse=False):
    if reverse:
        original = "".join(list(reversed(original.replace(f".{extension}", "").strip())))
        compare = "".join(list(reversed(compare.replace(f".{extension}", "").strip())))
    common = []
    limit = min((len(original), len(compare)))
    for i in range(0, limit):
        if original[i] != compare[i]:
            break
        common.append(original[i])
    if reverse:
        return "".join(list(reversed(common)))
    return "".join(common)

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
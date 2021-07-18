"""
    (c) 2020 Rodney Maniego Jr.
    Didak
    MIT License
"""

import os
import sys
import zipfile
import subprocess
from statistics import mean

from arkivist import Arkivist
from maguro import Maguro

def didak(directory, testcase, identifier, sensitive=0, unzip=0, convert=0, loops=99, reset=0):
    
    if not isinstance(directory, str):
        print("\nDidakError: 'directory' parameter must be a string.")
        return
    
    if not check_path(f"{directory}/didak"):
        os.makedirs(f"{directory}/didak")
    
    directory = directory.replace("\\", "/")
    if directory[-1] == "/":
        directory = directory[:-1]
    
    if not isinstance(identifier, str):
        print("\nDidakError: 'identifier' parameter must be a string.")
        return
    
    if not isinstance(loops, int):
        loops = 100

    sensitive = validate(sensitive, 0, 1, 0)
    unzip = validate(unzip, 0, 1, 0)
    convert = validate(convert, 0, 1, 0)
    loops = validate(loops, 1, 9999, 99)
    reset = validate(reset, 0, 1, 0)
    
    testcase_filename = ""
    if isinstance(testcase, str):
        if not check_path(testcase):
            print("\nDidakWarning: Test case file was not found.")
            testcase = None

    if testcase is not None:
        testcase = testcase.replace("\\", "/")
    
    
    if not check_path(f"{directory}/didak"):
        os.makedirs(f"{directory}/didak")
    
    if unzip == 1:
        files = get_filenames(directory, "zip")
        if len(files) > 0:
            print("\nUnzipping files:")
            for filename in files:
                print(f" - {filename}")
                extract(f"{directory}/{filename}", f"{directory}")
    
    if convert == 1:
        files = get_filenames(directory, "ipynb")
        if len(files) > 0:
            print("\nConverting notebooks:")
            for filename in files:
                print(f" - {filename}")
                ipynb2py(f"{directory}/{filename}")

    print("\nAnalyzing files...")
    
    prev = ""
    if testcase_filename is not None:
        testcase_filename = testcase.split("/")[-1:][0]

    analysis = Arkivist(f"{directory}/didak/analysis.json", sort=True)
    if reset == 1:
        analysis.clear()
    filenames = get_filenames(f"{directory}", "py")
    for filename in filenames:
        if identifier == "" or identifier in filename:
            metadata = analyze(directory, filename, testcase, sensitive, loops)
            analysis.set(filename, metadata)
    
    print("\nGenerating report...")
    
    count = 0
    analysis.reload()
    for filename, metadata in analysis.show().items():
        if identifier == "" or identifier in filename:
            count += 1
            score = metadata.get("score", 0)
            max = metadata.get("max", 0)
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
            print(f" - Current: {score} of {max}, Total: {total_score:,.2f}/{max_score:,.2f}")

def analyze(directory, filename, testcase, sensitive, loops):
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
        script = script.replace("\r", "")
        script = script.replace(" \n", "")
        script = script.replace(" \n", "")
        script = script.replace(" \n", "")
        script = script.replace(" \n", "")
        script = script.replace(" \n", "")
        script = script.replace(",\n", ",")
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
        loop_counters = 1
        previous = ""
        previous_indent = ""
        for line in script.split("\n"):
            line = line.rstrip()
            if line != "":
                line = line.replace(" (", "(")
                line = line.replace("while(", "while (")
                line = indent_correction(remove_comments(line))
                if previous in ("if", "else", "for", "while", "try", "except", "with", "def"):
                    if len(previous_indent) >= len(get_indents(line)):
                        line = f"    {line}"
                previous_indent_count = len(previous_indent) // 4
                current_indent_count = len(get_indents(line)) // 4
                if (current_indent_count - previous_indent_count) > 1:
                    line = line.strip()
                    for x in range((previous_indent_count+1)):
                        line = f"    {line}"
                
                command = list(line.strip().split(" "))[0].replace(":", "").strip()
                if command in ("while", "for"):
                    indents = get_indents(line)
                    formatted.append(f"{indents}didak_loop_counter{loop_counters} = 0")
                    formatted.append(line)
                    indents = get_indents(line, 1)
                    formatted.append(f"{indents}if didak_loop_counter{loop_counters} >= {loops}:")
                    indents = get_indents(line, 2)
                    formatted.append(f"{indents}print(\"Reached the maximum limit of recursion.\")")
                    formatted.append(f"{indents}break")
                    indents = get_indents(line, 1)
                    formatted.append(f"{indents}didak_loop_counter{loop_counters} += 1")
                    loop_counters += 1
                elif ("input(" not in line):
                    formatted.append(line)
                elif "=" in line:
                    found = False
                    keyword_index = 0
                    for key, value in keywords.items():
                        if found:
                            break
                        if key not in used:
                            for search in csv(key)[0]:
                                if search in line:
                                    variable = line.split("=")[0]                               
                                    if sensitive == 0:
                                        line = line.lower()
                                    values = []
                                    for x in variable.split(","):
                                        try:
                                            next_key = list(keywords.keys())[keyword_index]
                                            next_value = keywords.get(next_key, 0)
                                            values.append(next_value)
                                            used.append(next_key)
                                            keyword_index += 1
                                        except:
                                            pass
                                    tuple_of_values = ",".join(values)
                                    if len(values) == 1:
                                        formatted.append(f"{variable} = {tuple_of_values}")
                                    else:
                                        formatted.append(f"{variable} = [{tuple_of_values}]")
                                    used.append(key)
                                    found = True
                                    break
                        if not found:
                            # workaround only
                            variable = line.split("=")[0]
                            formatted.append(f"{variable} = 1")
                        keyword_index += 1
                else:
                    # workaround only
                    formatted.append(line.replace("input(", "print("))
                previous_indent = get_indents(line)
                previous = list(line.strip().split(" "))[0].replace(":", "")
        
        with open(f"{directory}/didak/test.py", "w+", encoding="utf-8") as file:
            file.write("\n".join(formatted))
        
        score = 0
        test_results = get_results(f"{directory}/didak/test.py")
        metadata.update({"results": test_results})
        if sensitive == 0:
            test_results = test_results.lower()
        results = list([x for x in results if len(x) > 0 and "".join(x) != ""])
        test_result_lines = list(test_results.split("\n"))
        test_result_lines = list([x for x in test_result_lines if x.strip() != ""])
        for result in results:
            if score >= len(test_result_lines):
                break
            for variant in result:
                if variant in test_results:
                    score += 1
                    break
        metadata.update({"score": score})
        metadata.update({"max": len(results)})
    return metadata

def ipynb2py(filepath):
    script = []
    ipynb = Arkivist(filepath).show()
    for cell in ipynb.get("cells", []):
        cell_type = cell.get("cell_type", "")
        outputs = cell.get("outputs", [])
        source = cell.get("source", [])
        
        if cell_type == "code" and len(outputs) > 0:
            for line in source:
                script.append(line)
            for line in outputs[0].get("text", 0):
                script.append(f"# {line}")
        else:
            for line in source:
                script.append(f"# {line}")
    new_filepath = filepath.replace(".ipynb", ".py")
    with open(new_filepath, "w+", encoding="utf-8") as file:
        if len(script) > 0:
            file.write("\n".join(script))

def grader(directory, tolerance=60):
    grades = Arkivist(f"{directory}/didak/grades.json", sort=True)
    abero_analysis = Arkivist(f"{directory}/abero/analysis.json")
    didak_analysis = Arkivist(f"{directory}/didak/analysis.json")
    for filename in didak_analysis.keys():
        statistics = abero_analysis.get(filename, {})
        originality = statistics.get("statistics", {}).get("originality", 100)
        metadata = didak_analysis.get(filename, {})
        common = ""
        total_score = metadata.get("score", 0) / metadata.get("max", 1)
        userdata = {}
        
        items = 1
        counter = 0
        for filename2, metadata2 in didak_analysis.show().items():
            if filename != filename2:
                if common == "":
                    temp = common_string(filename, filename2)
                    if len(temp) >= 10:
                        common = temp
                if common != "" and common in filename2:
                    items += 1
                    counter += 1
                    total_score += metadata2.get("score", 0) / metadata2.get("max", 1)
                    userdata = grades.get(common, {})
        
        if counter == 0:
            common = filename
        if common != "":
            uniqueness = userdata.get("originality", [])
            uniqueness.append(originality)
            userdata.update({"uniqueness": uniqueness})
            userdata.update({"score": total_score})
            userdata.update({"items": items})
            grades.set(common, userdata)

    originality = []
    for filename, userdata in grades.items():
        originality.append(round(mean(userdata.get("uniqueness", [0])), 2))

    common_originality = mean(originality)
    if tolerance == 50:
        tolerance = common_originality

    count = 1
    for filename, userdata in grades.items():
        grade = round(userdata.get("grade", 0), 2)
        originality = round(mean(userdata.get("uniqueness", [100])), 2)
        items = round(userdata.get("items", 1), 2)
        score = round(userdata.get("score", 0), 2)
        total = round((score / items * 100), 2)
        adjusted = total
        adjusted_score = score
        if originality < tolerance:
            adjusted = round((total * (originality / 100)), 2)
            adjusted_score = round((score * (originality / 100)), 2)
        
        print(f"\nFile #{count} - {filename}")
        print(f" - Originality: {originality}%")
        print(f" - Maximum grade: {score}/{items} ({total}%)")
        print(f" - Expected grade: {adjusted_score} ({adjusted}%)")
        userdata.update({"grade": adjusted_score})
        grades.set(filename, userdata)
        count += 1

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

def get_indents(line, add=0):
    spaces = []
    for character in line:
        if line[0] != " ":
            break
        if (len(spaces) > 1 and character != " "):
            break
        else:
            spaces.append(" ")
    indents = ["".join(spaces)]
    for x in range(add):
        indents.append("    ")
    return "".join(indents)

def indent_correction(line):
    line = line.replace("\t", "    ")
    indents = get_indents(line)
    spaces = len(indents) % 4
    while (len(indents) % 4) != 0:
        if spaces < 2:
            indents = indents[:-1]
        else:
            indents += " "
    return f"{indents}{line.strip()}"

def remove_comments(line):
    """
    double_quotes = line.count("\"") - line.count("\\\"")
    single_quotes = line.count("'") - line.count("\\'")
    
    if double_quotes == 0 and single_quotes == 0:
        return list(line.split("#"))[0]
    
    mod_double_quotes = double_quotes % 2
    mod_single_quotes = single_quotes % 2        
    
    if mod_single_quotes == 0 and single_quotes > 0:
        if "\"\"\"" not in line and "'" in line:
            line = line.replace("\"", "\\\"").replace("'", "\"")
    """
    
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

    
def defaults(value, minimum, maximum, fallback):
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

import abero
import didak
from arkivist import Arkivist

lab = "02"
directory = f"C:\\drive\\notebooks\\vsu\\2021S2_0315\\01 workload\\ESci 126\\codes\\lab\\{lab}\\Y034"
template = f"C:\\drive\\notebooks\\vsu\\2021S2_0315\\01 workload\\ESci 126\\codes\\lab\\{lab}\\control.py"
extension = "py"
threshold = 90
tolerance = 60
skipnames = 1
group = 1
convert = 1

abero.analyze(directory, extension, threshold, template, skipnames, group)


tests = ("1", "2", "3", "4", "5")
# tests = ("1", "2", "3a", "4a", "5")
for index, test in enumerate(tests):
    count = index + 1
    identifier = f"Q{count}"
    testcase = f"C:\\drive\\notebooks\\vsu\\2021S2_0315\\01 workload\\ESci 126\\codes\\lab\\{lab}\\testcaseq{test}.txt"
    didak.didak(directory, testcase, identifier, convert=convert)


didak.grader(directory, tolerance)
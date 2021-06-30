
import abero
import didak
from arkivist import Arkivist


directory = "C:\\drive\\notebooks\\vsu\\2021S2_0315\\01 workload\\ESci 126\\codes\\lab\\03\\G227"
template = "C:\\drive\\notebooks\\vsu\\2021S2_0315\\01 workload\\ESci 126\\codes\\lab\\03\\control.py"
extension = "py"
threshold = 90
tolerance = 60
skipnames = 1
group = 1

# abero.analyze(directory, extension, threshold, template, skipnames, group)


tests = ("1", "2", "3a", "4a", "5")
for index, test in enumerate(tests):
    count = index + 1
    identifier = f"Q{count}"
    testcase = f"C:\\drive\\notebooks\\vsu\\2021S2_0315\\01 workload\\ESci 126\\codes\\lab\\03\\testcaseq{test}.txt"
    didak.didak(directory, testcase, identifier)


didak.grader(directory, tolerance)
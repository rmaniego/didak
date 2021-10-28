import abero
import didak

template = "C:/drive/notebooks/work/vsu-dcst/2021,22S1_0823/workload/esci126/lab/2/control.py"
extension = "py"
threshold = 90
tolerance = 60
skipnames = 1
group = 1

offerings = ("G401",) # ("G401", "G402", "G403", "G404", "G405", "G406")
for offering in offerings:
    directory = f"C:/drive/notebooks/work/vsu-dcst/2021,22S1_0823/workload/esci126/lab/2/{offering}"

    abero.analyze(directory, extension=extension, threshold=threshold, template=template, skipnames=skipnames, group=group, unzip=1)

    tests = {"1": "1", "2": "2", "3": "3", "4a": "4", "4b": "4", "5a": "5", "5b": "5"}
    for test, num in tests.items():
        identifier = f"Q{num}"
        testcase = f"C:/drive/notebooks/work/vsu-dcst/2021,22S1_0823/workload/esci126/lab/2/q{test}.txt"
        print(testcase)
        didak.didak(directory, testcase, identifier, convert=1)

    didak.grader(directory, tolerance)
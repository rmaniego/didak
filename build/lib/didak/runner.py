import sys
import argparse

import didak


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
if not didak.check_path(directory):
    print(f"\nDidakError: The directory was not found: {directory}")
    sys.exit(0)

# get testcase path
testcase = args.testcase
if testcase is not None:
    if not didak.check_path(testcase):
        print(f"\nDidakWarning: File was not found: {testcase}")
        sys.exit(0)

# get identifier
identifier = args.identifier
if identifier is None:
    identifier = ""

# set the case-sensitive flag
sensitive = didak.defaults(args.sensitive, 0, 1, 0)

# set the unzip flag
unzip = didak.defaults(args.unzip, 0, 1, 0)

# set the clear data flag
reset = didak.defaults(args.reset, 0, 1, 0)

didak.didak(directory, testcase=testcase, identifier=identifier, sensitive=sensitive, unzip=unzip, reset=reset)
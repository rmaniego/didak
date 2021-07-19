# didak
Python is a basic test case runner, that simulates input and verifies the whether the final output is correct.

## Requirements
Didak uses the following packages:
- arkivist
- autopep8
- maguro

## Usage
Install the latest didak package, upcoming versions might introduce unannounced changes, so a virtual environment is a must have before installation.
```bash
pip install -U didak
```

To integrate didak into your Python codes, check the code snippet below:
```python
import didak

didak.didak(directory, testcase, identifier, sensitive=0, unzip=0, convert=0, loops=99, reset=0)
```

## CLI Usage
```bash
# usage: runner [-h] -d directory -t testcase [-i identifier] [-s sensitive] [-u unzip] [-c convert] [-l loops] [-r reset]

py runner.py -d "<path_to_files>" -t "<path_to_testcase>" -i "<keyword>" -s 1 -u 1 -c 1 -l 99 -r 1
```

1. `-d <path>` - Full path of the dirctory containing the files to execute.
2. `-t <*.txt>` - Path to test case file
3. `-u <0>` - Unzip/extract ZIP files (0-1; default = 0)
4. `-c <0>` - Convert Jupyter notbooks to Python file (0-1; default = 0)
5. `-i <keyword>` - Unique keyword found on files to execute
6. `-s <0>` - Case-sensitivity (0-1; default = 0)
7. `-l <99>` - Looping / max recursions (1-9999; default = 99)
8. `-r <0>` - Reset analytics before execution (0-1; default = 0)

## Test Case
Is used to fill in expected input and function parameters before execution and verifying of expected output.
** Template*
```csv
"Keyword1", "keyword1", "keyword 1" = value1
"Keyword2", "keyword2", "keyword 2" = value1
...
"Keyword3", "keyword3", "keyword 3" = value1
---
"Result1", "result1", "result 1"
"Result2", "result2", "result 2"
...
"Result3", "result3", "result 3"
```

**Sample**
```csv
"keyword1", "key" = "name"
"abcde", "abc" = 23.7
...
"qwerty", "qwe" = False
---
"Hello, name!", "hello, name!"
"76.87", "76.9", "77"
```

## Did you know?
The repository name `didak` was inspired from the words deduce and Didache; deduce means to arrived at a consluion by reasoning, while Didache is a manuscript in the Christain theological literature.
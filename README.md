# didak
Python is a basic test case runner, that simulates input and verifies the whether the final output is correct.

## Requirements
- [Arkivist](https://pypi.org/project/arkivist/) `pip install arkivist`
- [Maguro](https://pypi.org/project/maguro/) `pip install maguro`


## Usage
```bash
# usage: didak [-h] -d directory -t testcase [-u unzip] [-i identifier] [-s sensitive] [-r reset]

py didak.py -d "<path_to_files>" -t "<path_to_testcase>" -u 1 -i "<keyword>" -s 1 -r 1
```

**1.** `-d <path>` - Full path of the dirctory containing the files to execute.
**1.** `-t <*.txt>` - Path to test case file
**2.** `-u <0>` - Unzip/extract ZIP files (0-1; default = 0)
**3.** `-i <keyword>` - Unique keyword found on files to execute
**4.** `-s <0>` - Case-sensitivity (0-1; default = 0)
**5.** `-r <0>` - Reset analytics before execution (0-1; default = 0)

## Test Case
Is used to fill in expected input and function parameters before execution and verifying of expected output.
** Template*
```csv
keyword1 = value1
keyword2 = value2
...
keyword3 = value3
---
result1
result2
...
result3
```

**Sample**
```csv
"keyword1", "key" = "name"
"abcde", "abc" = 23.7
...
"qwerty", "qwe" = False
---
hello, name!
76.3
```

## Did you know?
The repository name `didak` was inspired from the words deduce and Didache; deduce means to arrived at a consluion by reasoning, while Didache is a manuscript in the Christain theological literature.

# Alias Analysis

We say that two pointers, p0 and p1, are aliases if they can point to the same memory location.
Alias analysis is a "may" static analysis that approximates the set of memory locations that each pointer can point to.
Thus, the goal of this analysis is to build a table, henceforth called an
*environment* that associates each pointer *p* with the memory locations that
*p* can point to.
The goal of this lab is to implement an Anderson-style points-to analysis, following the techniques seen in the [classroom](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/PointerAnalysis.pdf).

## The Assignment

The goal of this lab is to finish the implementation of [alias.py](alias.py).
This file contains one method `abstract_interp`, which you must implement.
This method receives as input a list of instructions, and returns the environment of points-to information created by these instructions.
In addition to the instructions in our previous labs, we shall have to deal with four new kinds of instructions:

1. `v = alloca`:
2. `v = move w`:
3. `*v = w`:
4. `w = *v`:

## Uploading the Assignment

Students enrolled in DCC888 have access to UFMG's grading system, via [Moodle](https://moodle.org/).
You must upload four python files to have your assignment graded: [driver.py](driver.py), [lang.py](lang.py), [parser.py](parser.py) and
[alias.py](alias.py).
Remember to click on "*Avaliar*" to have your assignment graded.

## Testing without Moodle

As in the previous labs, all the files in this exercise contain `doctest` comments.
You can easily test your implementation by doing, for instance:

```
python3 -m doctest alias.py
```

This lab also provides a [folder](tests) with some test cases.
To simulate automatic grading, you can run [drive.py](driver.py) directly, e.g.:

```
python3 driver.py < tests/ref0.txt
```

In this exercise, the driver prints the table of points-to information.
# Introduction to Data-Flow Analyses

The goal of this lab is to introduce students to concepts related to
[data-flow analyses](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/IntroDataFlow.pdf).
Students shall have contact with two types of data-flow analyses:
[liveness analysis](https://en.wikipedia.org/wiki/Live-variable_analysis) and [Reaching-Definitions Analysis](https://en.wikipedia.org/wiki/Reaching_definition).

## The Assignment

To solve this lab, you will have to have solved the [previous lab](../Parsing), that asked for the implementation of the parser.
Thus, as a preliminary step, rename your parser, from the previous lab, from `todo.py` to `parser.py`.
Notice that this lab contains a file [parser.py](parser.py), which you can replace with the `todo.py` from the previous lab (well, assuming that you have implemented it, of course).
The parser is the only file from the previous lab that you should reuse.

The goal of this lab is to implement liveness analysis.
Liveness analysis is a "*backward*" data-flow analysis, meaning that information propagates along the opposite direction through which the program flows.
It is also a "*may*" analysis, meaning that information is an over-approximation of facts that might happen in the program (to make things simpler, the join/meet operation is set-union).
If you want to recap how the analysis works, check out the [course material](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/IntroDataFlow.pdf).

In addition of filling up the code in [parser.py](parser.py), you will have to implement [dataflow.py](dataflow.py) (no `todo.py` in this lab!).
There are two classes that you must implement: `LivenessAnalysisIN_Eq` and `LivenessAnalysisOUT_Eq`.
These classes represent data-flow equations.
Additionally, you will have to implement function `liveness_constraint_gen`, which maps instructions to equations.
As an example, you can use an implementation of reaching-definition analysis, also available in the file `dataflow.py`.

Notice that a data-flow analysis is essentially a system of equations.
These are the equations that you must implement.
In terms of implementation, these equations work pretty much like instructions: 
they contain an `eval` method.
In your case, this method is rather called `eval_aux`.
The evaluation of an equation affects an environment: a table that associates equations with data-flow facts.
In the case of liveness analysis, the data-flow facts are the variables alive at some program point.
Solving a data-flow analysis is equivalent to "interpreting" these equations, as if they were actual instructions, until the environment that contains the data-flow facts stops changing, e.g.:

```
def interp_abstractly(equations):
    env = {} # initially empty
    changed = True
    while changed:
        changed = False
        for eq in equations:
            changed = changed or eq.eval(env)
```

And from where these equations come from? They are extracted from the program! That is what the `liveness_constraint_gen` function will do (and that's what the example `reaching_defs_constraint_gen` does.)

## Uploading the Assignment

Students enrolled in DCC888 have access to UFMG's grading system, via [Moodle](https://moodle.org/).
You must upload four python files to have your assignment graded: [driver.py](driver.py), [lang.py](lang.py), [parser.py](parser.py) and
[dataflow.py](dataflow.py).
Remember to click on "*Avaliar*" to have your assignment graded.

## Testing without Moodle

As in the previous labs, all the files in this exercise contain `doctest` comments.
You can easily test your implementation by doing, for instance:

```
python3 -m doctest dataflow.py
```

This lab also provides a [folder](tests) with some test cases.
To simulate automatic grading, you can run [drive.py](driver.py) directly, e.g.:

```
python3 driver.py < tests/fib.txt
```

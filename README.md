# Introduction to Static Program Analyses

This repository holds some of the project assignments used in DCC888 -
Introduction to Program Analysis, a course offered by the Department of
Computer Science of the Federal University of Minas Gerais, as part of the
courses of UFMG's [Compilers Lab](https://lac-dcc.github.io/).
For the course material, check its [website](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888). A full list of the topics covered is available in the
[syllabus](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/).

## Building and Running

This webpage contains a few labs: short project assignments. In practice, these assignments are automatically graded using [UFMG's Moodle](https://sistemas.ufmg.br/portal/render.userLayoutRootNode.uP).
However, the labs can be used independently.
They are all implemented in Python.
Each program contains lots of doctests.
Thus, to test, say, your implementation of `dataflow.py`, just do:

```
python3 -m doctest dataflow.py
```

Additionally, most of the labs contain a folder called `tests`, with some text files that you can run using the main routine, in `driver.py`, e.g.:

```
python3 driver.py < tests/fib.txt
```

## Table of Contents

The following labs are available:

### Control-Flow Graphs

In this [lab](/ControlFlowGraphs), the student will create simple [control-flow
graphs](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/ControlFlowGraphs.pdf) using a toy, assembly-like, programming language.

### Parsing

In this [lab](/Parsing), the student will create a small parser that will
convert text files into control-flow graphs.

### Data-Flow Analysis

In this [lab](/IntroDataFlow), the student will implement [liveness analysis](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/IntroDataFlow.pdf) and run this implementation onto our toy language.

### Worklist Algorithms

In this [lab](/Worklist), the student will implement a [worklist-based](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/WorkList.pdf) solver for dataflow analyses.


### Dominators

In this [lab](/Dominance), the student will implement a data-flow analysis to compute the [dominance tree](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/LoopOptimizations.pdf) of a program.


### Semantics of Phi-Functions

In this [lab](/PhiFunctions), the student will add phi-functions to our toy three-address code language, so that we can write programs in [Static Single-Assignment Form](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/StaticSingleAssignment.pdf).

### Constant Propagation

In this [lab](/ConstantPropagation), the student will implement the sparse data-flow equations for [constant propagation](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/SparseAbstractInterpretation.pdf).
The student will use the results of this analysis to remove some instructions (those whose value can be computed at compilation time) from the program.

### Alias Analysis

In this [lab](/AliasAnalysis), the student will implement a version of Andersen-style Alias Analysis, following the lecture notes seen in [class](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/PointerAnalysis.pdf).


### Type Checking

In this [lab](/TypeChecking), the student will implement Type-Checking to verify if programs are **Safe**, as seen in [class](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/TypeSystems.pdf)

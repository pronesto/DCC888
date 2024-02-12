# Static Single-Assignment Form

[Static Single-Assignment](https://en.wikipedia.org/wiki/Static_single-assignment_form) (SSA) Form is a program representation similar to three-address code, but with a fundamental difference: each variable is assigned at only one program location.
SSA form programs enjoy an important property: the definition site of a variable dominates every use of that variable.
In practical terms, SSA is more of a notation than an actual program implementation; however, it is still possible to interpret these programs.
In this exercise, we shall do exactly this: write an interpreter for SSA-form programs.
We shall try two approaches: first, we will give some semantics to phi-functions, and then we will see that we, in fact, need more: to correctly implement the semantics of phi-functions, we need to evaluate them as parallel copies.
This lab refer to the class on static single-assignment form, which is part of the [material](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/StaticSingleAssignment.pdf) covered in the classroom.

## The Assignment

This assignment has two parts.
In the first part, we shall implement a "tentative" semantics for phi-functions.
I say tentative because it will only work for a very special flavor of SSA-form programs: the so-called programs in *Conventional Static Single-Assignment (CSSA)
Form*.
CSSA-form programs have the following definition, which we quote from the paper [SSA Elimination after Register Allocation](https://homepages.dcc.ufmg.br/~fernando/publications/papers/CC09.pdf): *A program is in CSSA form if no two variables related by phi-functions have overlapping live ranges*.
Figure 1 below explains the notion of phi-related variables with examples.

![Example of CSSA-form programs](../assets/images/phiRelated.png)

This tentative semantics for phi-functions will be implemented as follows:
given a phi-function such as `a0 = phi(a1, ..., an)`, we shall find, in the environment, the latest binding for any of the variables in the set `{a1, ..., an}`, and then assign this value to `a0`.
The class `Phi` is already implemented for you.
Notice that this class invokes a method on the environment called `get_from_list`.
In this assignment, you will have to implement this method.
To help you understand how this semantics works, take a look into Figure 2 below:

![Running the factorial function](../assets/images/ssaFact.png)

This semantics will work fine for CSSA-form programs.
And it is rather elegant: we do not need to keep track of the path used to reach a phi-function: the last binding within its list of uses will be always the correct assignment!
However, this semantics will collapse for non-CSSA form programs.
And these programs do exist.
Most algorithms that create SSA form will in fact create CSSA-form programs.
However, some compiler optimizations might propagate copies, breaking the conventional property.
That is what happened in Figure 1-d.
In this case, we start having issues like the infamous "swap problem" and the "lost-copy problem" which Preston Briggs described in the early days of [SSA designing](https://homes.luddy.indiana.edu/achauhan/Teaching/B629/2006-Fall/CourseMaterial/1998-spe-briggs-ssa_improv.pdf).
Figure 3 illustrates the swap problem.

![The Swap Problem](../assets/images/ssaPrograms.png)

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

As an example, the program in Figure 2 can be tested using the series of Python statements seen in Figure 3.

![Example of doctest for dominance relation](../assets/images/testDominance.png)

This lab also provides a [folder](tests) with some test cases.
To simulate automatic grading, you can run [drive.py](driver.py) directly, e.g.:

```
python3 driver.py < tests/fib.txt
```

In this exercise, the driver prints the dominance tree of each program.
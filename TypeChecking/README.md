# Type Checking

If a language's syntax supports Type rules, the program can be type-checked to avoid [**stuck states**](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/TypeSystems.pdf). **Stuck states** happen when a program must execute an operation with incompatible data, here seen as an instruction with incorrect types. Similarly to semantic rules, a program may be interpreted according to the type rules. If the program does not encounter a **stuck state**, it is sound, or **Safe**. A type-safe program has guaranteed *Progress* and *Preservation*.

- *Progress* implies that no instruction gets stuck: they can always be evaluated.
- *Preservation* implies that the program always progresses from a type-safe state to a type-safe state.

## Pre-Requisites

In order to pass every test in this assignment you are expected to have solved the [Phi-Function](../PhiFunctions/) lab and the [Parsing](../Parsing) lab.
Make sure your parser exists in a file called `parser.py`.

## The Assignment

In this lab we must build a simple type-checker in the model language. In order to do this, a new set of features has been implemented onto [lang.py](lang.py):

- A new `TypeEnv` class extends the `Env` class and is used for type-checking.
- A new `InstTypeErr` exception to be raised when a given program has a type-invalid instruction
- The `Read` instruction has been split into the typed instructions ReadNum and ReadBool
- All instructions (`Add`, `Mul`, `Lth`, `Geq`, `Bt`, `Phi`, `PhiBlock`, `ReadNum`, `ReadBool`) have a `type_eval` method.
- A new global `type_check` function was added to [lang.py](lang.py).

In order to implement the type-checker, all `type_eval` methods must be implemented.
If an instruction fails to type check, then an `InstTypeErr` exception must be raised.
Type checking happens at the `type_check` function, which is already implemented for you.
This function iterates over the list of instructions and, by using `type_eval`, verifies if the whole program is sound.
The implementation of `type_eval` follows the type checking rules in Figure 1.

![Type checking rules](../assets/images/type_checking.png)

## Uploading the Assignment

Students enrolled in DCC888 have access to UFMG's grading system, via [Moodle](https://moodle.org/).
You must upload three python files to have your assignment graded: [driver.py](driver.py), [lang.py](lang.py) and [parser.py](parser.py)
Remember to click on "*Avaliar*" to have your assignment graded.

## Testing without Moodle

As in the previous labs, all the files in this exercise contain `doctest` comments.
You can easily test your implementation by doing, for instance:

```
python3 -m doctest lang.py
```

This lab also provides a [folder](tests) with some test cases.
To simulate automatic grading, you can run [drive.py](driver.py) directly, e.g.:

```
python3 driver.py < tests/fib.txt
```
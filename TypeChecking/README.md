# Type Checking
If a language's syntax supports Type rules, the program can be type-checked to avoid [**stuck states**](https://homepages.dcc.ufmg.br/~fernando/classes/dcc888/ementa/slides/TypeSystems.pdf). **Stuck states** happen when a program must execute an operation with incompatible data, here seen as an instruction with incorrect types. Similarly to semantic rules, a program may be interpreted according to the type rules. If the program does not encounter a **stuck state**, it is sound, or **Safe**. A type-safe program has guaranteed *Progress* and *Preservation*.

- *Progress* implies that no instruction gets stuck: they can always be evaluated.
- *Preservation* implies that the program always progresses from a type-safe state to a type-safe state.

## The Assignment
In this lab we must built a simple type-checker in the model language. In order to do this, a new set of features has been implemented:
- A new TypeEnv extends the Env class and is restricted for type-checking.
- A new InstTypeErr describes when a given program has a type-invalid instruction
- Read instruction has been split into the typed instructions ReadNum and ReadBool
- All instructions (Add, Mul, Lth, Geq, Bt, Phi, PhiBlock, ReadNum, ReadBool) have a `type_eval` method.
- A new global `type_check` function.

In order to implement the type-checker, all `type_eval` methods must be implemented. If an instruction instance leads up to a stuck state, an `InstTypeErr` exception must be raised. Furthermore, the `type_check` function must iterate over the program and, by using `type_eval`, verify if the whole program is sound. Be mindful of Phi and PhiBlock instructions.

Besides the `driver.py` and `lang.py` modules, the following files are required:
- A [parser implementation](../Parsing).
- [phi functions](../PhiFunctions) should be fully implemented.

Thus, as a preliminary step, rename your parser, from that lab, from `todo.py` to `parser.py`. In order to have functional Phi functions, their `eval` methods may be copied from previous exercises - our goal is to maintain a usable language.

The model language's type rules can be formalized as:
![Model Language Type Rules](../assets/images/typerules.png)


## Uploading the Assignment

Students enrolled in DCC888 have access to UFMG's grading system, via [Moodle](https://moodle.org/).
You must upload four python files to have your assignment graded: [driver.py](driver.py), [lang.py](lang.py) and [parser.py](parser.py)
Remember to click on "*Avaliar*" to have your assignment graded.

## Testing without Moodle

As in the previous labs, all the files in this exercise contain `doctest` comments.
You can easily test your implementation by doing, for instance:

```
python3 -m doctest lang.py
```

As an example, the following program is included in the Doctests:

![Example of doctest for dominance relation](../assets/images/constantpropexample.png)

This lab also provides a [folder](tests) with some test cases.
To simulate automatic grading, you can run [drive.py](driver.py) directly, e.g.:

```
python3 driver.py < tests/fib.txt
```

# What the port found in the compiler

The plan listed what the port might need from `ceu-atmos`. What the
work found, in the order it was found:

## Worked around

- **A field named as a keyword in a constructor**: `[loop=false]` is a
  syntax error, while `d.loop` and data files with `loop = false` work.
  The options of `Sprite` became `once` and `cycle`.
- **A native literal with one backquote is one line**: a call that
  spans lines must be on one line, or use three backquotes.
- **A nested `func` is a global**: `func f` inside a task declares a
  variable of the main chunk, as the manual says, so two sprites shared
  their `advance`, and a closure over a pinned table escaped. Nested
  functions are `val func`.
- **`emit @(:parent)` from a task in a pool reaches the pool**, the
  siblings of the task, and not the task that holds the pool. The
  buttons of the actions rely on it (they select and unselect each
  other); the dots of the worldmap receive the view as an argument, and
  emit to it (`emit @v`). The manual says only "parent task": the case
  of pools may deserve a line there.
- **`await x` of a variable** needs the value form, `await(x)`.
- **`loop n { }`** is not a counted loop: `loop _ in n { }`.
- **A string with an escaped delimiter** (`"a\"b"`) is still a syntax
  error; `'"'` is used instead.
- **Iterating a tagged table** gives the field `tag` among the items:
  an index of data (a tagged vector) is iterated by position.

## Measured

- **Speed**: a task wake costs about 55 ns (2000 tasks, 1000 events,
  0.11 s). The game with 100 pingus and fast forward runs at 500 frames
  per second with the software renderer, which takes most of the time.
- **`X.load`**: 2 ms for the largest level (334 KB). No cache needed.
- **Build time**: 24 s for the whole game (one C file, `-O2`). The tests
  build the game once. A faster build (`-O1`, or separate compilation
  of the libraries in Atmos) would help the edit-run loop.
- **The address sanitizer** finds no error and no leak in the tests.

## Not needed

- Name clashes of `include`: none in 60 files, with prefixes by unit
  (`wm_`, `basher_`, `pg.`).
- The tree of tasks in the error traces: the errors were found with the
  traces of calls, and the trace of actions of the game (`PINGUS_TRACE`).

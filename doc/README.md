# The case study: C++, Céu, Atmos

The study "Structured Synchronous Reactive Programming for Game
Development: On Rewriting Pingus from C++ to Céu" (SBGames 2018, full
text at <https://fsantanna.github.io/pingus>) names five control-flow
patterns of games, and shows each one in C++ and in Céu. These
documents add the third column: the same cases in Atmos, in this port.

| Pattern | Case | Document |
|---------|------|----------|
| Finite state machines | the *Armageddon* button double click | [armageddon.md](armageddon.md) |
| Finite state machines | the *Bomber* action | [bomber.md](bomber.md) |
| Continuation passing | advancing pages in the *Story* screen | [story.md](story.md) |
| Continuation passing | from *Story* to *Credits*, and the other transitions | [transitions.md](transitions.md) |
| Dispatching hierarchies | the *Bomber* `draw` and `update` | [dispatching.md](dispatching.md) |
| Lifespan hierarchies | the game UI widgets, the pingus container | [lifespan.md](lifespan.md) |
| Signaling mechanisms | pausing the world, global keys and the options | [signaling.md](signaling.md) |

And the measures:

- [state.md](state.md): the state variables of each unit, in C++, Céu,
  and Atmos.
- [loc.md](loc.md): lines of code per part.
- [todo.md](todo.md): the open issues of the Céu rewrite, in this port.
- [bench.md](bench.md): memory, CPU and frames of the port.

The C++ code is quoted by the study, with links to the pinned commit of
the original. The Céu code is at `fsantanna/pingus@036852a`, in `ceu/`.
The Atmos code is in this repository.

## The construct mapping

| Céu | Atmos |
|-----|-------|
| `code/await X (...) -> T` | `task X (...) { ... }`, the result is the last value |
| `await X(...)` | `await X(...)` |
| `spawn X(...) in pool` | `spawn @pool X(...)` |
| `pool[] X xs` | `pin xs = tasks()` |
| `par/or`, `par/and`, `par` | `par :any`, `par :all`, `par` |
| `watching e do ... end` | `watching e { ... }` |
| `every e do ... end` | `loop on e { ... }` |
| `await FOREVER` | `await(false)` |
| `escape v` | `return v`, the last value, or `break v` |
| `do ... finalize ... end` | `defer { ... }` |
| `event T e`, `emit e(v)`, `await e` | `emit :e [v]`, `await :e` (tags) |
| `pause/if e do ... end` | `toggle t(false)`, `toggle on :e { ... }` |
| `var&` alias to data of another unit | a table shared by reference, or `pub` |
| `outer.x` | a variable captured by the closure, or an argument |

# Lifespan hierarchies

## The game UI widgets

### C++

`GameSession` creates the widgets in its constructor (button panel,
pingus counter, small map), adds them to a container of the GUI
manager, and they are destroyed with it
([study, section "Game UI Widgets"](https://fsantanna.github.io/pingus/#game-ui-widgets)).

### Céu

The widgets are blocks of a `par` in the game: they live as long as
the game.

### Atmos

`game/game.atm`:

```
spawn SmallMap(g)
spawn Time(g)
spawn Counters(g)
spawn Armageddon(g)
spawn FastForward(g)
spawn Pause(g)
pin buttons = tasks()
loop i, a in acts {
    spawn @buttons ActionButton(g, i, a, #acts)
}
spawn ActionKeys(g, acts)
spawn Playfield(g)
```

An unassigned `spawn` is pinned to the enclosing block: the widgets
live as long as the game task. The action buttons are many, so they
live in a pool, pinned in the same block.

## The pingus container

### C++

`PinguHolder` keeps a list of pingus, with explicit add and remove, and
deletes the dead ones by hand
([study, section "The Pingus Container"](https://fsantanna.github.io/pingus/#the-pingus-container)).

### Céu

`pool[] Pingu pingus;` in the game: a pingu is spawned in the pool, and
leaves it when its code terminates.

### Atmos

`game/game.atm` and `game/objs/entrance.atm`:

```
pin pingus = tasks()
<...>
spawn @(g.pingus) Pingu(g, x, y, d, owner)
```

The `Pingu` task returns `:exited` or `:dead`, and its pool frees it.
The pools of particles, smoke, and weather work the same: a particle
ends with its time, and is gone.

## Discussion

- The lifespan is the block: when the game task ends, every pingu,
  particle, object and widget ends with it, and the ground maps are
  released by a `defer` of the game. Between two levels nothing
  survives but the progress (a table saved with `X.dump`).
- The open issue of Céu "at each restart, twice the pingus are created"
  (`ceu/TODO.md`) cannot happen: the pool of pingus is pinned in the
  game, and is a new one for each game.
- A table of the game, `g`, is pinned in the same block as the pools,
  and holds them: the objects that need the pingus (the exits, the
  traps, the blocker) receive `g`. The rules of `pin` check that none
  of them escapes the game: a pool cannot be stored in a table that
  lives longer than it.
- The tasks of a pool are only referred to while iterating it
  (`loop _, t in g.pingus`), or by a local of a task that lives inside
  the game. The traps (spike, teleporter) iterate the pool at the tick
  they act, and keep no reference to a pingu across ticks.

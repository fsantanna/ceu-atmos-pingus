# Dispatching hierarchies: the *Bomber* `draw` and `update`

Every object of the game must update itself at each frame, and draw
itself in the right order.

## C++

The bomber has a sprite member, and forwards to it the calls of
`update` and `draw`, which it receives from the pingu, which receives
them from the pingu holder, which receives them from the world, which
receives them from the game session, which receives them from the
screen manager. Each class in the chain forwards the calls by hand
([study, section "Dispatching Hierarchies"](https://fsantanna.github.io/pingus/#dispatching-hierarchies)).

## Céu

The bomber spawns a `Sprite`, which reacts to `dt` and `redraw` by
itself, while it is alive:

```
code/await Bomber (void) -> _ActionName__Enum do
    var&? Sprite_from_name sprite = spawn Sprite_from_name(<...>);
    <...>
end
```

## Atmos

`engine/engine.atm`, the task `Sprite`, and its use in
`game/pingu/actions/bomber.atm`:

```
task Sprite (name, pos, o) {
    <...>
    par :any {
        <...the frames advance with the time...>
        loop on :tick {
            until advance(33)
        }
    } with {
        loop on :sdl.draw {
            pg.part(k.img, <...the frame...>, pos.x - cam.x - k.dx, pos.y - cam.y - k.dy)
        }
    }
}

task Bomber (p, g) {
    pin s = spawn Sprite(pspr(p, "bomber/left"), p, PSPR1)
    <...>
}
```

## Discussion

- As in Céu, there is no `draw` nor `update` to forward: every task
  awaits `:sdl.draw` and the time (`:tick`, or `:clock`) itself. The
  tree of tasks is the dispatch.
- The draw order is the order of the tree: the game pins its layers as
  pools, in order (backgrounds, the ground, liquids and exits,
  particles, pingus, front objects, traps, weather), then spawns the
  panel. A task in a pool is drawn after the pools pinned before it.
  This answers the open issues of z-order of the Céu rewrite: the order
  is fixed by the structure of the game task, not by each object.
- The time of the world is an event of the game, `:tick`, which the
  clock of the game emits. The sprites of the world advance with it,
  and the sprites of the screens with `:clock`, the time of the
  environment: pausing the world stops the first and not the second
  (see [signaling.md](signaling.md)).
- The sprite of a pingu follows the direction of the pingu when it is
  drawn (the option `turn`), instead of a task that watches the
  direction and restarts the sprite (`RightLeftSprites` of Céu).

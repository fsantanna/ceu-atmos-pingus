# Signaling mechanisms

## Pausing the world

A click on the *Pause* button, or the key `P`, pauses the objects of
the world (pingus, traps, particles), but not the panel, whose buttons
keep working and whose animations keep moving.

### C++

The world checks a flag `is_paused` in each `update`, and the pause
button reads the same flag to draw itself
([study, section "Pausing the World"](https://fsantanna.github.io/pingus/#pausing-the-world)).

### Céu

The game loop does not emit the update of the world while
`is_paused` is set: a state variable, toggled by an event.

### Atmos

`game/game.atm`: the time of the world comes from a task, the `Clock`,
which emits `:tick` to the game. Pausing the world is pausing that
task with `toggle`:

```
pin clock = spawn Clock()

;; pause: the clock stops; a single step gives one tick
spawn {
    loop {
        val e = await <:game.pause || :game.step>
        toggle clock(false)
        if e ?? :game.step {
            emit :tick
        }
        par :any {
            await <:game.pause || :game.ff.on>
        } with {
            loop on :game.step {
                emit :tick
            }
        }
        toggle clock(true)
    }
}
```

The *Pause* button shows the state in its code position
(`game/hud.atm`):

```
loop {
    watching :game.pause {
        spawn Sprite("core/buttons/hbuttonbgb", r)
        await Click(r)
        emit @(:parent) :game.pause
    }
    watching :game.pause {
        spawn Sprite("core/buttons/hbuttonbg", r)
        await Click(r)
        emit @(:parent) :game.pause
    }
}
```

- No flag: paused or not is where the code of the pause task is, and
  the button knows it in the same way.
- The world is not paused object by object: it stops receiving time.
  The objects and the pingus are the same tasks, awaiting `:tick`, and
  the panel keeps reacting to the mouse and to the time of the screen.
- Fast forward is the same clock in another mode: 4 ticks per 20ms.
  The mode is the position in the code of the clock, a loop of two
  `watching` blocks.

## Global keys and the options menu

`F5`, or the *Options* button of the menu, shows the options over any
screen, and pauses that screen while they are shown.

### C++

The screen manager keeps a stack of screens and pushes the options
screen on the top; the screen below does not receive events.

### Céu

`ceu/main.ceu`: the screens are in a `pause/if go_pause` block, and a
`par` branch awaits the key and emits `go_pause(true)` before showing
the options.

### Atmos

`main.atm`:

```
par :any {
    toggle on :screens {
        <...the menu and the screens...>
    }
} with {
    loop {
        await <:go.options || :sdl.key.dn [name="F5"]>
        emit :screens [false]
        await Options()
        emit :screens [true]
    }
} with {
    await :sdl.quit
}
```

- `toggle on :screens` is the `pause/if` of Céu. When off, the block
  receives no event at all, not even `:sdl.draw`: the paused screen is
  not drawn, and the options take the screen.
- The menu asks for the options with a global event,
  `emit @(:global) :go.options`, since the menu is a task deep inside
  the paused block, and the options are outside it.

# The *Armageddon* button double click

A double click in the *Armageddon* button explodes all pingus: the
second click must come within 1 second of the first.

## C++

`ArmageddonButton` keeps two state variables, `pressed` and
`press_time`, which the callbacks `on_click` and `update` share: the
first click sets `pressed`, `update` counts the time and resets both
after 1 second, and a click with `pressed` set is the double click.
The accesses to the variables are 40 lines apart in the class
([study, section "Finite State Machines"](https://fsantanna.github.io/pingus/#finite-state-machines-1)).

## Céu

`ceu/pingus/screens/game/input.ceu`:

```
loop do
    await component.component.on_primary_button_pressed;
    watching 1s do
        await component.component.on_primary_button_pressed;
        break;
    end
end
...
emit outer.game.go_armageddon;
```

## Atmos

`game/hud.atm`, the task `Armageddon`:

```
task Armageddon (g) {
    val r = [x=W-44, y=H-65, w=38, h=60]
    val pos = [x=r.x+19, y=r.y+30]
    spawn Sprite("core/buttons/hbuttonbgb", r)
    do {
        spawn Sprite("core/buttons/armageddon_anim", pos, [anchor=:center, still=true, frame=7])
        loop {
            await Click(r)
            watching 1s {
                await Click(r)
                break
            }
        }
    }
    spawn Sprite("core/buttons/armageddon_anim", pos, [anchor=:center])
    emit @(:parent) :game.armageddon
    await(false)
}
```

## Discussion

- The structure is the one of Céu: a loop that awaits a click, and a
  `watching 1s` that awaits the second one. No state variable.
- `Click(r)` is itself a task: a press and a release inside `r`. The
  widget of Céu (`RectComponent`) signals events that the button
  awaits; in Atmos the click is awaited as a task, which returns when
  it happens. The button has no events of its own.
- The images of the button are the code position: the still image
  lives in the `do` block of the loop, and the animated one after it.
  When the loop breaks, the block ends, and with it the still sprite.
- The effect goes out by an event to the game, as in Céu. In Atmos it
  is a tag, `:game.armageddon`, emitted to the parent task, which is
  the game: the entrances, the goal, and the armageddon of the pingus
  await it.
- The key `A` does the same with no double click: it emits the same
  event (`game/game.atm`).

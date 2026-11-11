# State variables

`cmp/state.md` of the Céu rewrite classifies the fields of each unit of
the C++ game. This table repeats it, with a third column: what each
variable is in Atmos.

The classes:

- **data**: a value of the game (position, velocity, direction): it
  stays, as a field or a local.
- **control**: only says what to do next (`sound_played`, a phase): it
  is removed, the position in the code holds it.
- **period**: counts frames to act every N updates (`delay_count`): it
  is removed, a loop awaits N ticks (`Ticks(n)`).
- **dual**: data of a sprite that its users read to decide (the frame,
  "is finished"): it is removed from the users, the sprite signals its
  frames (`:frame [n]`) and terminates when it ends.
- **action**: `set_action(x)`: it is removed, the action returns the
  next one.

The review rule of the port: a `var` that is only read by an `if` or a
`match` to decide what to do next is a state variable, and is either
justified in a comment, or removed.

## Pingu actions

| Unit | Variable (C++) | Class | Céu | Atmos |
|------|----------------|-------|-----|-------|
| Basher | sprite | dual | spawn, reads `frame` | `Sprite`, awaits `:frame` |
| | basher_c | period | `loop i`, `await dt` x3 | `Ticks(3)` |
| | first_bash | control | var | the first bash before the loop |
| | set_action() | action | `escape` | the result of the task |
| Blocker | sprite | data | spawn | `Sprite` |
| Bomber | sprite | dual | reads `frame` | awaits `:frame` |
| | particle_thrown, sound_played, gfx_exploded, colmap_exploded | control | sequence | sequence |
| Bridger | walk_sprite, build_sprite | dual | reads `frame`, awaits end | awaits `:frame`, awaits the sprite |
| | block_build | control | `await` | `await` |
| | bricks | data | var | the loop index; `p.bricks` for the display |
| | mode | control | sequence | sequence |
| Climber | sprite | data | spawn | `Sprite` |
| Digger | delay_count | period | `i%4` | `loop k in 4`, `await :tick` |
| Drown | sprite | dual | awaits end | awaits the sprite |
| Exiter | sound_played | control | on start | on start |
| Faller | faller, tumbler | dual | `await dt until tumbling` | `watching :tick until tumbling(p)` |
| | mover | data | `Mover` signals `ok_collided` | `Mover` signals `:collided` |
| Floater | sprite | data | spawn | `Sprite` |
| Jumper | sprite | data | spawn | `Sprite` |
| Laserkill | sprite | dual | awaits end | awaits the sprite |
| Miner | delay_count | period | `i%4`, `i%2` | `await :tick`, `Ticks(3)` |
| Slider | speed | data | var | var |
| Splashed | particle_thrown | control | on start | on start |
| Waiter | countdown | period | var, `-0.025` per update | `Ticks(81)` |
| Walker | floaterlayer | dual | `await dt until fall_action` | `await :tick until p.fall` |

## World objects

| Unit | Variable (C++) | Class | Céu | Atmos |
|------|----------------|-------|-----|-------|
| Spike | surface | dual | awaits | `await(s)` |
| | killing | control | --- | `par :any`, the kill at `:frame 3` |
| Guillotine | sprite_kill_r/l, sprite_idle | dual | awaits | awaits |
| | direction | data | --- | the result of the idle phase |
| | killing | control | --- | sequence: idle, then kill |
| Entrance | last_release | period | var, `game_time` | `Ticks(rate)` |
| | last_direction | control | var `last_was_right` | a loop over `[1, -1]` |
| LaserExit | killing | control | --- | sequence: idle, then zap |
| Smasher | smashing, downwards | control | sequence | sequence |
| | count | period | local | the sprite, one frame per tick |
| Hammer (new) | down, count | control | (none in Céu) | sequence: down, smash, up |
| FakeExit (new) | smashing | control | (none in Céu) | sequence: idle, then smash |
| IceBlock (new) | thickness | data | (none in Céu) | `ice.thick`, drawn |
| | last_contact, finished | control | (none in Céu) | a loop that awaits 50 ticks with no contact; `return` |
| SwitchDoor (new) | opening, current_height | control, data | (none in Céu) | `await :door.open`; `door.h`, drawn |
| SwitchDoorSwitch (new) | triggered | control | (none in Céu) | sequence: one `await`, then forever |
| Teleporter (new) | clock | dual | (none in Céu) | awaits the sprite |

## Particles, panel, game

| Unit | Variable (C++) | Class | Céu | Atmos |
|------|----------------|-------|-----|-------|
| PinguParticle | livetime | period | `loop i in [0->livetime[` | `loop _ in n` |
| | particles | lifespan | pool | pool |
| SmokeParticle | livetime | period | loop | loop |
| SmallMap | scroll_mode | control | --- | `watching :sdl.mouse.up` |
| SmallMapImage | update_count | period | var | the C map rebuilds on change |
| Playfield | mouse_scrolling | control | --- | `watching :sdl.mouse.up until it.but == 3` |
| Armageddon | pressed, press_time | control | loop, `watching 1s` | loop, `watching 1s` |
| PauseButton | is_paused | control | var in `input.ceu` | the code position (`toggle clock`) |
| FastForward | is_fast_forwarded | control | var in `input.ceu` | the code position of the clock |
| | do_single_step | control | var | `emit :tick` |
| GoalManager | in_armageddon | control | var | `await :game.armageddon` in a branch |
| Pingu | current_action | action | var | the loop; `p.act` published for observers |
| | wall_action, fall_action | data | var | `p.wall`, `p.fall` |
| | previous_action | data | var | an argument of the next action |

## Counts

Variables that only decide what to do next (classes control, period,
dual on the side of the users, action), in the units above:

| | C++ | Céu | Atmos |
|-|-----|-----|-------|
| Pingu actions (17) | 24 | 5 (`delay_count` x2, `countdown`, `first_bash`, frames read) | 0 |
| World objects of Céu (10) | 13 | 3 (`last_release`, `last_was_right`, frames read) | 0 |
| Panel and game | 9 | 4 (`is_paused`, `is_fast_forwarded`, `do_single_step`, `in_armageddon`) | 0 |

What remains mutable in Atmos is data, each one listed with the reason:

- `p.act` (`game/pingu/pingu.atm`): the current action, written by the
  loop of actions for the observers (the playfield shows it, the
  armageddon and the traps ask it). The pingu itself does not read it
  to decide: the action that runs is the position in the loop. `Go`
  reads it to check if an order is allowed, which is the table
  `CHANGE_ALLOWED` of the original.
- `var act, prev` in the loop of actions: the result of the previous
  action, which is the next one to run.
- `g.next`: the action selected by the player, which the buttons show.
- velocities, positions, counters of the panel, the frame of a sprite
  (inside the sprite), the thickness of an ice block, the height of a
  door, the letters shown of a story: data that is drawn.
- `late` of the clock: the time not yet given to the world.

# The *Bomber* action

A bomber counts down with an animation of 16 frames, plays a sound at
the frame 10, and explodes at the frame 13: particles, a hole in the
ground, and the explosion image for a moment. Then the pingu dies.

## C++

`Bomber` keeps 4 flags, one per effect that must happen once:
`sound_played`, `particle_thrown`, `colmap_exploded`, `gfx_exploded`.
`update` checks the current frame of the sprite at each call, and the
flags avoid repeating each effect while the frame stays the same
([study, section "The Bomber Action"](https://fsantanna.github.io/pingus/#the-bomber-action)).

## Céu

`ceu/pingus/screens/game/pingu/actions/bomber.ceu`:

```
var&? Sprite_from_name sprite = spawn Sprite_from_name(..., "/bomber/left", ...);
watching sprite do
    spawn Mover();
    await outer.game.dt until sprite.sprite.frame == 10;
    call {Sound::PingusSound::play_sound}("plop", 0.5, 0.0);
    await outer.game.dt until sprite.sprite.frame == 13;
    loop i in [0 -> 50[ do
        spawn PinguParticle(...) in outer.pingu_particles;
    end
    call Game_Remove({&bomber_radius}, ...);
    do
        spawn Sprite_from_name(&outer.pingu.rect, ".../explo", &outer.game.dt);
        await outer.game.dt;
    end
end
escape {ActionName::DEAD};
```

## Atmos

`game/pingu/actions/bomber.atm`:

```
task Bomber (p, g) {
    sound("ohno", 0.5)
    pin s = spawn Sprite(pspr(p, "bomber/left"), p, PSPR1)
    par :any {
        await(s)
    } with {
        await Mover(p)
    } with {
        await :frame until it.n == 10
        sound("plop", 0.5)
        await :frame until it.n == 13
        loop _ in 50 {
            spawn @(g.particles) PinguParticle(g, p.x, p.y - 5)
        }
        val gfx = res_surface("other/bomber_radius_gfx")
        val col = res_surface("other/bomber_radius")
        val w, h = pg.size(col)
        ground_remove(gfx, col, p.x - (w//2), p.y - (w//2) - 16)
        spawn Sprite(pspr(p, "explo"), p, PSPR1)
        await :tick
    }
    :dead
}
```

## Discussion

- The sequence of effects is the sequence of the code, as in Céu: no
  flags.
- In Céu, the action awaits each update and reads the frame of the
  sprite: `await dt until sprite.frame == 10`. The frame is a field of
  the sprite that its users read, which `cmp/state.md` of the study
  calls a "dual" variable: data for the sprite, control for its users.
  In Atmos, the sprite signals each new frame to its parent task,
  `:frame [n]`, and the bomber awaits the event:
  `await :frame until it.n == 10`. The frame is no longer read from
  outside.
- `watching sprite` of Céu (the bomber ends if the animation ends) is a
  branch of the `par :any` that awaits the sprite task: `await(s)`.
- The mover is a task that moves the pingu with its velocity at each
  tick, and signals collisions, which the bomber ignores.
- The action returns `:dead`: the pingu loop ends the pingu.

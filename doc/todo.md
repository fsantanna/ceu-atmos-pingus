# The open issues of the Céu rewrite

`ceu/TODO.md` of `fsantanna/pingus@036852a` lists the open issues of the
Céu rewrite. Each one, in this port: **fixed**, **gone** (the problem
cannot happen by construction), **open**, or **out** (out of scope).

| Issue (Céu) | Port | How |
|-------------|------|-----|
| smallmap viewport vs total rectangles do not match (snow17) | fixed | the view is drawn from `CAM` and the size of the level, with the same scale as the map |
| pause/fwd with mouse/buttons have bugs | fixed | the clock of the world is paused with `toggle`, and the buttons follow the events `:game.pause`, `:game.ff.on/off` (tested in `tst/clicks.sh`) |
| gfx: menu icebergs, fade, credits below blackboard | fixed (icebergs, credits) | the layers of the menu move; the credits are only drawn inside the board |
| BUG: playfield lines, background does not repeat | fixed | the background is tiled in both directions, with its parallax |
| TODO: configuration of input events, controllers | out | the keys of the original are fixed in `game/game.atm` |
| TODO: cursor | open | the system cursor is used |
| TODO: fast forward in the worldmap | open | |
| TODO: border of the worldmap | open | |
| TODO: read/write inputs (demos) | out | demos are out of the plan |
| cache of sprites, or performance is not viable | fixed | images are loaded once, in a cache of `engine/pingus.h`; sprite descriptions in `DESCS` |
| countdown action disable from the original | gone | no countdown actions in the data |
| walker behind all | fixed | draw order is the order of the pools in the game |
| BUG: at each restart, twice the pingus are created | gone | the pool of pingus is pinned in the game, a new one per game |
| BUG: `is_world=false` in sprite.ceu | gone | a sprite of the world is an option, `world=true`, which selects its camera and its time |
| BUG: clicks on the pingus | fixed | the nearest pingu under the mouse, as the original (tested) |
| BUG: background of the pingu counter fixed | fixed | it is drawn at the top center |
| BUG: small map behind the water of snow20 | gone | the panel is spawned after all the layers of the world |
| BUG: the fall of the pingu out of the entrance is slightly off | open | to compare with the original |
| BUG: periodic glitch in the smallmap related to RENDER | gone | the small map is a texture rebuilt when the collision map changes |
| BUG: small glitch in the smallmap at the start of the level | gone | same |
| z-order front entrance snow-tutorial, front entrance behind the pingu | fixed | hotspots with z >= 100 go to the front layer, after the pingus |
| TODO: pos_offset in all objects in factory | fixed | prefabs and groups are resolved by the loader, with their offsets |
| color.a in surface_background | fixed | the color is drawn over the background |
| idle laser_exit | fixed | the laser exit is still, until a pingu enters it |
| EXIT/LASER_EXIT take only 1 at a time | fixed | each tick checks all the pingus |
| EXITER/LASERKILL in pingu.ceu | fixed | they are actions, as the others |
| BUG: climber center | open | to compare with the original |
| global:world.pingus will simplify min.ceu | gone | the pingus are a pool of the game, which receive the game `g` |
| bug of the WORLD_UPDATE needed | gone | `:tick` is an event of the game, emitted by its clock |
| bridger offset | open | the bridger is drawn at the pingu, with no extra offset |
| test climber, wall-mode activation | fixed | `tst/levels.txt`: climber |
| test previous action: Climber->Jumper->..., Blocker->Faller->Blocker | partly | the previous action is an argument of the next action; the wall jump (climber, then jumper) is tested (`walljump` in `tst/levels.txt`); blocker, faller, blocker is not |
| SDL_DT for pingus/actions/sprites | gone | world sprites use `:tick`, screen sprites use `:clock` |

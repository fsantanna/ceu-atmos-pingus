#!/usr/bin/env python3

# Lines of code and tokens of what was ported, per unit, in the C++ of
# the official game, in the Céu rewrite, and in this port.
#
#   tools/loc.py OFFICIAL CEU [--files]
#
#   OFFICIAL  checkout of Pingus/pingus at ffe3851
#   CEU       checkout of fsantanna/pingus at 036852a (the Céu rewrite)
#
# A line of code is a line that is not blank, not only a comment, and
# not a line of the preprocessor (#include, header guards). A token is
# an identifier, a number, a string, a tag (:name), or an operator,
# after the comments are removed. The C++ counts include the headers.

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ACTIONS_COMMON = ["basher", "blocker", "bomber", "bridger", "climber",
    "digger", "drown", "exiter", "faller", "floater", "jumper",
    "laser_kill", "miner", "slider", "splashed", "waiter", "walker"]
ACTIONS_NEW = ["angel", "boarder", "smashed", "superman"]

OFF = sys.argv[1] if len(sys.argv) > 2 else "."
CEU = sys.argv[2] if len(sys.argv) > 2 else "."

def rglob (base, pat):
    return sorted(os.path.relpath(f, base) for f in glob.glob(os.path.join(base, pat)))

def atm_action (a):
    return "game/pingu/actions/%s.atm" % a.replace("_", "")

def cpp (*names):
    return ["src/" + n + e for n in names for e in (".cpp", ".hpp")]

# unit: (C++ of the official game, Céu, Atmos)
UNITS = []
for a in ACTIONS_COMMON:
    UNITS.append(("action " + a, cpp("pingus/actions/" + a),
        ["ceu/pingus/screens/game/pingu/actions/%s.ceu" % a], [atm_action(a)]))
for a in ACTIONS_NEW:
    UNITS.append(("action " + a, cpp("pingus/actions/" + a), None, [atm_action(a)]))

UNITS += [
    ("pingu core", cpp("pingus/pingu", "pingus/pingu_action",
            "pingus/action_name", "pingus/action_holder", "pingus/pingu_holder",
            "pingus/mover", "pingus/movers/linear_mover", "pingus/collider",
            "pingus/colliders/pingu_collider", "pingus/direction",
            "pingus/groundtype", "pingus/capture_rectangle",
            "pingus/particles/pingu_particle_holder",
            "pingus/particles/smoke_particle_holder")
            + ["src/pingus/pingu_enums.hpp", "src/pingus/ecs/pingus.cpp"],
        ["ceu/pingus/screens/game/pingu/pingu.ceu",
         "ceu/pingus/screens/game/pingu/mover.ceu",
         "ceu/pingus/screens/game/pingu/codes.ceu",
         "ceu/pingus/screens/game/pingu/capture_rectangle.ceu",
         "ceu/pingus/screens/game/pingu/pingu_particle.ceu",
         "ceu/pingus/screens/game/pingu/smoke_particle.ceu",
         "ceu/pingus/screens/game/actions.ceu",
         "ceu/pingus/screens/game/codes.ceu",
         "ceu/pingus/screens/game/capture_rectangle.ceu"],
        ["game/pingu/pingu.atm", "game/pingu/actions.atm",
         "game/pingu/particles.atm", "game/pingu/actions/dead.atm"]),
    ("world objects, weather", ["src/pingus/ecs/" + f for f in (
            "objects.cpp", "traps.cpp", "effects.cpp", "weather.cpp",
            "object_factory.cpp", "components.hpp", "systems.cpp",
            "systems.hpp", "system_parts.hpp")]
            + cpp("pingus/particles/rain_particle_holder",
                  "pingus/particles/snow_particle_holder"),
        rglob(CEU, "ceu/pingus/screens/game/objs/*.ceu"),
        ["game/objs.atm"] + rglob(ROOT, "game/objs/*.atm")),
    ("game: world, panel, playfield, level, ground", cpp("pingus/world",
            "pingus/screens/game_session", "pingus/components/action_button",
            "pingus/components/button_panel", "pingus/components/pingus_counter",
            "pingus/components/playfield", "pingus/components/smallmap",
            "pingus/components/time_display", "pingus/smallmap_image",
            "pingus/goal_manager", "pingus/game_time", "pingus/ground_map",
            "pingus/collision_map", "pingus/collision_mask",
            "pingus/pingus_level", "pingus/plf_res_mgr", "pingus/prefab_file",
            "pingus/server") + ["src/pingus/pingus_level_impl.hpp"],
        ["ceu/pingus/screens/game/" + f for f in ("game.ceu",
            "goal_manager.ceu", "input.ceu", "pingus_counter.ceu",
            "playfield.ceu", "smallmap.ceu", "smallmap_image.ceu",
            "time_display.ceu")],
        ["game/game.atm", "game/hud.atm", "game/playfield.atm",
         "game/level.atm", "game/ground.atm"]),
    ("screens: menu, start, result, story, credits, levels, worldmap",
        cpp("pingus/screens/pingus_menu", "pingus/screens/start_screen",
            "pingus/screens/result_screen", "pingus/screens/story_screen",
            "pingus/screens/credits", "pingus/screens/level_menu",
            "pingus/components/menu_button", "pingus/layer_manager",
            "pingus/levelset", "pingus/savegame", "pingus/savegame_manager",
            "pingus/stat_manager", "pingus/global_event")
            + rglob(OFF, "src/pingus/worldmap/*.[ch]pp"),
        ["ceu/" + f for f in ("main.ceu", "pingus/global_event.ceu",
            "pingus/screens/menu/menu.ceu", "pingus/screens/menu/button.ceu",
            "pingus/screens/start.ceu", "pingus/screens/result.ceu",
            "pingus/screens/story.ceu", "pingus/screens/credits.ceu",
            "pingus/screens/wood.ceu", "pingus/screens/levels/levels.ceu",
            "pingus/screens/levels/levelsets.ceu", "pingus/screens/levels/menu.ceu",
            "pingus/screens/worldmap/aux.ceu", "pingus/screens/worldmap/dots.ceu",
            "pingus/screens/worldmap/pingus.ceu",
            "pingus/screens/worldmap/sprite_drawable.ceu",
            "pingus/screens/worldmap/worldmap.ceu")],
        ["main.atm", "screens/common.atm", "screens/menu.atm",
         "screens/start.atm", "screens/result.atm", "screens/story.atm",
         "screens/credits.atm", "screens/levels.atm", "screens/worldmap.atm"]),
]

# apart: the options (the port has no choice of renderer), and the
# engine of the port is its own C over SDL2
OTHERS = [
    ("options (all but the renderer)", cpp("pingus/screens/option_menu",
            "pingus/components/label", "pingus/components/check_box",
            "pingus/components/choice_box", "pingus/components/slider_box"),
        rglob(CEU, "ceu/pingus/screens/options/*.ceu"),
        ["screens/options.atm"]),
    ("engine (C++ engine / Céu engine / C + Atmos)", None,
        rglob(CEU, "ceu/engine/*/*.ceu") + ["ceu/rrect.ceu",
            "ceu/pingus/right_left_sprites.ceu"],
        ["engine/pingus.h", "engine/sdl.atm", "engine/engine.atm"]),
]

TOKEN = re.compile(r'''
    "(?:\\.|[^"\\])*"              # string
  | '(?:\\.|[^'\\])*'              # char
  | :[A-Za-z_][\w.\-]*             # tag (Atmos), or a C++ scope colon + name
  | [A-Za-z_]\w*                   # identifier
  | \d+(?:\.\d+)?(?:[eE][-+]?\d+)?[fFuUlL]*  # number
  | ::|->|\+\+|--|<<|>>|<=|>=|==|!=|&&|\|\||=>|\+=|-=|\*=|/=|//
  | \S                             # any other punctuation
''', re.X)

def strip (text, lang):
    if lang == "atm":
        # ;; comments to the end of the line, ;;; blocks ;;;
        text = re.sub(r";;;.*?;;;", "", text, flags=re.S)
        lines = [re.sub(r";;.*", "", l) for l in text.split("\n")]
    else:
        text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"),
                      text, flags=re.S)
        lines = [re.sub(r"//.*", "", l) for l in text.split("\n")]
        lines = [l for l in lines if not l.strip().startswith("#")]
    return [l for l in lines if l.strip()]

def count (files, base):
    loc = tok = 0
    for f in files:
        p = f if os.path.isabs(f) else os.path.join(base, f)
        if not os.path.exists(p):
            continue
        lang = "atm" if p.endswith(".atm") else "c"
        lines = strip(open(p, encoding="utf-8", errors="replace").read(), lang)
        loc += len(lines)
        for l in lines:
            if lang == "c":
                # in C++ and Céu, a ':' after a name is not a tag
                tok += len(re.findall(TOKEN, l.replace(":", " : ").replace(" :  : ", "::")))
            else:
                tok += len(re.findall(TOKEN, l))
    return loc, tok

def missing (files, base):
    return [f for f in files if not os.path.exists(
        f if os.path.isabs(f) else os.path.join(base, f))]

def engine_cpp (off):
    return [f for f in glob.glob(os.path.join(off, "src/engine/**/*"), recursive=True)
            if f.endswith((".cpp", ".hpp"))]

def main ():
    off, ceu = sys.argv[1], sys.argv[2]
    show = "--files" in sys.argv
    print("| Unit | C++ lines | Céu lines | Atmos lines | C++ tokens | Céu tokens | Atmos tokens |")
    print("|------|-----------|-----------|-------------|------------|------------|--------------|")
    tot = {}
    def row (name, c, e, a, total):
        cl, ct = count(c, off) if c is not None else (None, None)
        el, et = count(e, ceu) if e is not None else (None, None)
        al, at = count(a, ROOT)
        if show:
            for base, fs in ((off, c), (ceu, e), (ROOT, a)):
                if fs is not None and missing(fs, base):
                    print("missing:", missing(fs, base), file=sys.stderr)
        f = lambda v: "---" if v is None else str(v)
        print("| %s | %s | %s | %s | %s | %s | %s |" %
              (name, f(cl), f(el), f(al), f(ct), f(et), f(at)))
        if total:
            for k, v in (("cl", cl), ("el", el), ("al", al), ("ct", ct), ("et", et), ("at", at)):
                tot[k] = tot.get(k, 0) + (v or 0)
        return cl, el, al, ct, et, at
    sub = {}
    for u in UNITS:
        r = row(*u, True)
        if u[0].startswith("action") and u[2] is not None:
            sub = {i: sub.get(i, 0) + r[i] for i in range(6)}
    print("| **total, game logic** | **%(cl)d** | **%(el)d** | **%(al)d** | **%(ct)d** | **%(et)d** | **%(at)d** |" % tot)
    for u in OTHERS:
        c = u[1] if u[1] is not None else engine_cpp(off)
        row(u[0], c, u[2], u[3], False)
    print()
    print("17 actions in common: C++ %d / Céu %d / Atmos %d lines, %d / %d / %d tokens"
          % (sub[0], sub[1], sub[2], sub[3], sub[4], sub[5]))

if __name__ == "__main__":
    main()

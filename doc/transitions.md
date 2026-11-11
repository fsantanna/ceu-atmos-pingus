# Transitions between screens

The transitions between screens are a case of continuation passing:
when a screen ends, what comes next depends on how it was reached.
From the worldmap, a story dot shows the *Story*, and the ending story
goes on to the *Credits*, and back to the worldmap.

## C++

Each screen pushes, replaces, or pops screens in a stack of the screen
manager. The *Story* receives a flag that tells it to replace itself by
the *Credits* when it ends (`StoryDot`, `StoryScreenComponent`): the
screens know each other
([study, section "Transition to the Credits"](https://fsantanna.github.io/pingus/#transition-to-the-credits-screen-from-the-story-screen)).

## Céu

`ceu/pingus/screens/worldmap/worldmap.ceu`: the worldmap is a loop
that awaits the choice of the player, and calls the next screen:

```
loop do
    var int ret = await Worldmap();
    if ret == STORY then
        var bool is_click = await Story();
        if is_click and credits then
            await Credits();
        end
    else/if ...
end
```

## Atmos

`screens/worldmap.atm`, the task `Worldmap`:

```
loop {
    music(wm.head.music)
    val n = await WmView(wm)
    until n == nil
    if n.level {
        val final = wm_solved(wm.nodes@(wm.head.final_node))
        await Play(n.level)
        if !final && wm_solved(wm.nodes@(wm.head.final_node)) && wm.end_story {
            await Story("data/" ++ wm.end_story ++ ".atm")
            await Credits()
        }
    } else {
        await Story(n.story)
        if n.credits {
            await Credits()
        }
    }
}
```

And the others, in the same direct style:

- `main.atm`: the menu, then the chosen screen, in a loop:
  `match await Menu() { :story => await Worldmap(...) ... }`.
- `screens/result.atm`, `Play`: the start screen, then the game and
  its result, again while the player retries:

```
task Play (path) {
    val lvl = level_load(path)
    if await Start(lvl) {
        loop {
            val r = await Game(path)
            level_store(path, r)
            val again = await Result(r)
            until !again, r
        }
    } else {
        nil
    }
}
```

- `screens/levels.atm`, `LevelsetsMenu`: the levelsets, then the levels
  of one, then a level, with a loop at each level of the menus.

## Discussion

- As in Céu, a screen is a task that returns what the player chose, and
  the next screen is the next line. The screens do not know each other:
  `Story` does not know that `Credits` may come after it.
- The result of a task is its last value: `await Story(...)` is the
  value of the story, and `await WmView(wm)` is the node chosen, or nil
  to leave. No continuation flags, no stacks of screens.
- The view of the worldmap is a task that ends when the player chooses
  something, and is created again after it. The position of the pingu
  is the only state that survives, and it is data: it is saved with the
  progress.

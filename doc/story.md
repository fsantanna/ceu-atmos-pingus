# Advancing pages in the *Story* screen

The *Story* screen shows pages: an image and a text written letter by
letter. A click on *next* shows the whole text at once, if it is still
being written, or goes to the next page.

## C++

`StoryScreenComponent` keeps the current page, the text displayed so
far, and the time, in member variables. `update` writes the text, and
`next_text` checks whether the text is complete to either complete it
or advance the page, popping it from a vector of pages
([study, section "Advancing Pages"](https://fsantanna.github.io/pingus/#advancing-pages-in-the-story-screen)).

## Céu

`ceu/pingus/screens/story.ceu`:

```
loop i in [0 <- {pages.size()}[ do
    <...the image of the page...>
    par/or do
        watching next_text do
            loop do
                var int dt = await outer.main.dt;
                time = time + dt;
                <...text = the first `time*0.02` letters...>
                if cur >= max then
                    break;
                end
            end
        end
        <...text = the whole text...>
        await next_text;
    with
        every outer.main.redraw do
            <...draws `text`...>
        end
    end
end
```

## Atmos

`screens/story.atm`:

```
loop _, page in st.pages {
    <...the image of the page...>
    val shown = [n=0, t=0]
    spawn {
        loop on :sdl.draw {
            text(FONT.chalk_normal, string.sub(txt, 0, shown.n - 1), ...)
        }
    }
    par :any {
        loop us on :clock {
            set shown.t += us / 1000
            set shown.n = math.min(#txt, trunc(shown.t * 0.02))
            until shown.n >= #txt
        }
    } with {
        await Button(nr, "core/misc/next", "core/misc/next_hover", "core/misc/next")
    } with {
        await :sdl.key.dn until X.xin(it.name, ["F", "Space", "Return"])
    }
    set shown.n = #txt
    par :any {
        await Button(nr, "core/misc/next", "core/misc/next_hover", "core/misc/next")
    } with {
        await :sdl.key.dn until X.xin(it.name, ["F", "Space", "Return"])
    }
}
```

## Discussion

- The two phases of a page (writing, then waiting) are two sequential
  blocks, as in Céu. The page is the iteration of the loop: there is no
  current page variable, and the end of the pages is the end of the
  loop.
- `shown` is the data of the drawing: how many letters are visible. It
  is not read to decide what to do next.
- Céu uses an event `next_text`, emitted by the *next* button and by the
  key. In Atmos the button is a task that returns when clicked: the
  phase awaits it directly, or the key, in a `par :any`. The event is
  gone, because the button is awaited where it is needed.
- The *next* button exists twice, once per phase, as a new task each
  time. Its lifetime is the one of the phase.

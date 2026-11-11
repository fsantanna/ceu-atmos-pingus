// The C side of the engine of the game.
//
// It is included by `engine/sdl.atm`, in a prelude, after the header of
// the runtime of Atmos. It holds what is not game logic, and what works
// per pixel:
//
//   - the driver: window, the loop of frames, and the events of SDL;
//   - images: loading, modifiers (rotations and flips), and a cache by
//     name, so that an image is loaded once;
//   - drawing: images, rectangles, lines;
//   - bitmap fonts, from the `.font` descriptions;
//   - sounds and music;
//   - the ground: the collision map (a ground type per pixel) and the
//     ground map (its image), with put and remove through masks;
//   - the test mode, with no screen, scripted keys and mouse, and
//     screenshots.
//
// Values cross to Atmos as numbers: an image or a font is an index in
// a table of this file, which lives until the program ends.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
#include <SDL2/SDL_mixer.h>

static SDL_Window*   PG_WIN = NULL;
static SDL_Renderer* PG_REN = NULL;
static int           PG_W   = 800;
static int           PG_H   = 600;
static int           PG_SND = 0;        // audio is open
static int           PG_TEST = 0;       // test mode: fixed frames

static int pg_int (AVal v) {
    return a_isnum(v) ? (int) a_dbl(v) : 0;
}

static const char* pg_cstr (AVal v) {
    return (v.type == A_STR) ? A_STR_OF(v)->s : NULL;
}

///////////////////////////////////////////////////////////////////////////////
// IMAGES
///////////////////////////////////////////////////////////////////////////////

typedef struct {
    char*         key;
    SDL_Surface*  sfc;      // RGBA32, kept for masks
    SDL_Texture*  tex;      // created on the first draw
    int           w, h;
} PgImg;

#define PG_IMGS_MAX 4096
static PgImg PG_IMGS[PG_IMGS_MAX];
static int   PG_IMGS_N = 0;

// The modifiers of the data files, as numbers:
//   0 ROT0  1 ROT90  2 ROT180  3 ROT270
//   4 ROT0FLIP  5 ROT90FLIP  6 ROT180FLIP  7 ROT270FLIP
static SDL_Surface* pg_modify (SDL_Surface* src, int mod) {
    int w = src->w, h = src->h;
    int swap = (mod==1 || mod==3 || mod==5 || mod==7);
    int W = swap ? h : w;
    int H = swap ? w : h;
    SDL_Surface* dst = SDL_CreateRGBSurfaceWithFormat(0, W, H, 32, SDL_PIXELFORMAT_RGBA32);
    uint32_t* s = src->pixels;
    uint32_t* d = dst->pixels;
    int sp = src->pitch / 4;
    int dp = dst->pitch / 4;
    for (int y=0; y<h; y++) {
        for (int x=0; x<w; x++) {
            int col, row;
            switch (mod) {
                case 1:  col = h-y-1; row = x;       break;
                case 2:  col = w-x-1; row = h-y-1;   break;
                case 3:  col = y;     row = w-x-1;   break;
                case 4:  col = w-x-1; row = y;       break;
                case 5:  col = y;     row = x;       break;
                case 6:  col = x;     row = h-y-1;   break;
                case 7:  col = h-y-1; row = w-x-1;   break;
                default: col = x;     row = y;       break;
            }
            d[row*dp + col] = s[y*sp + x];
        }
    }
    return dst;
}

// Loads an image, crops it to `cw x ch` at `cx,cy` (if `cw>0`), and
// applies a modifier. Returns its index, or -1.
static int pg_img_load (const char* path, int mod, int cx, int cy, int cw, int ch) {
    if (path == NULL) {
        return -1;
    }
    char key[1024];
    snprintf(key, sizeof(key), "%s#%d#%d,%d,%d,%d", path, mod, cx, cy, cw, ch);
    for (int i=0; i<PG_IMGS_N; i++) {
        if (!strcmp(PG_IMGS[i].key, key)) {
            return i;
        }
    }
    if (PG_IMGS_N == PG_IMGS_MAX) {
        return -1;
    }
    SDL_Surface* raw = IMG_Load(path);
    if (raw == NULL) {
        return -1;
    }
    SDL_Surface* sfc = SDL_ConvertSurfaceFormat(raw, SDL_PIXELFORMAT_RGBA32, 0);
    SDL_FreeSurface(raw);
    if (sfc == NULL) {
        return -1;
    }
    if (cw > 0 && ch > 0) {
        SDL_Surface* sub = SDL_CreateRGBSurfaceWithFormat(0, cw, ch, 32, SDL_PIXELFORMAT_RGBA32);
        SDL_Rect r = { cx, cy, cw, ch };
        SDL_SetSurfaceBlendMode(sfc, SDL_BLENDMODE_NONE);
        SDL_BlitSurface(sfc, &r, sub, NULL);
        SDL_FreeSurface(sfc);
        sfc = sub;
    }
    if (mod != 0) {
        SDL_Surface* m = pg_modify(sfc, mod);
        SDL_FreeSurface(sfc);
        sfc = m;
    }
    SDL_SetSurfaceBlendMode(sfc, SDL_BLENDMODE_BLEND);
    PgImg* img = &PG_IMGS[PG_IMGS_N];
    img->key = strdup(key);
    img->sfc = sfc;
    img->tex = NULL;
    img->w   = sfc->w;
    img->h   = sfc->h;
    return PG_IMGS_N++;
}

static PgImg* pg_img (int i) {
    return (i>=0 && i<PG_IMGS_N) ? &PG_IMGS[i] : NULL;
}

static SDL_Texture* pg_tex (PgImg* img) {
    if (img->tex == NULL && PG_REN != NULL) {
        img->tex = SDL_CreateTextureFromSurface(PG_REN, img->sfc);
        SDL_SetTextureBlendMode(img->tex, SDL_BLENDMODE_BLEND);
    }
    return img->tex;
}

// Draws the part `sx,sy,sw,sh` of an image at `dx,dy`, with the
// same size, or at `dw x dh` if given.
static void pg_img_draw (int i, int sx, int sy, int sw, int sh, int dx, int dy, int dw, int dh, int alpha) {
    PgImg* img = pg_img(i);
    if (img == NULL || PG_REN == NULL) {
        return;
    }
    if (sw <= 0) { sx = 0; sy = 0; sw = img->w; sh = img->h; }
    if (dw <= 0) { dw = sw; dh = sh; }
    if (dx >= PG_W || dy >= PG_H || dx+dw <= 0 || dy+dh <= 0) {
        return;     // out of the screen
    }
    SDL_Texture* tex = pg_tex(img);
    SDL_Rect s = { sx, sy, sw, sh };
    SDL_Rect d = { dx, dy, dw, dh };
    if (alpha < 255) {
        SDL_SetTextureAlphaMod(tex, alpha<0 ? 0 : alpha);
    }
    SDL_RenderCopy(PG_REN, tex, &s, &d);
    if (alpha < 255) {
        SDL_SetTextureAlphaMod(tex, 255);
    }
}

///////////////////////////////////////////////////////////////////////////////
// SHAPES
///////////////////////////////////////////////////////////////////////////////

static void pg_color (int64_t rgba) {
    SDL_SetRenderDrawBlendMode(PG_REN, SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(PG_REN, (rgba>>24)&0xFF, (rgba>>16)&0xFF,
                                   (rgba>>8)&0xFF, rgba&0xFF);
}

static void pg_fill (int64_t rgba, int x, int y, int w, int h) {
    if (PG_REN == NULL) return;
    pg_color(rgba);
    SDL_Rect r = { x, y, w, h };
    SDL_RenderFillRect(PG_REN, &r);
}

static void pg_rect (int64_t rgba, int x, int y, int w, int h) {
    if (PG_REN == NULL) return;
    pg_color(rgba);
    SDL_Rect r = { x, y, w, h };
    SDL_RenderDrawRect(PG_REN, &r);
}

static void pg_line (int64_t rgba, int x1, int y1, int x2, int y2) {
    if (PG_REN == NULL) return;
    pg_color(rgba);
    SDL_RenderDrawLine(PG_REN, x1, y1, x2, y2);
}

///////////////////////////////////////////////////////////////////////////////
// FONTS
///////////////////////////////////////////////////////////////////////////////

typedef struct {
    int16_t x, y, w, h;     // in the image
    int16_t ox, oy;         // offset of the drawing
    int16_t adv;            // advance
    int16_t img;            // the image, or -1 if absent
} PgGlyph;

typedef struct {
    PgGlyph* glyphs;        // by unicode, 65536
    int      size;
    float    char_spacing;
    float    vertical_spacing;
} PgFont;

#define PG_FONTS_MAX 16
static PgFont PG_FONTS[PG_FONTS_MAX];
static int    PG_FONTS_N = 0;

static int pg_font_new (int size, double cs, double vs) {
    if (PG_FONTS_N == PG_FONTS_MAX) {
        return -1;
    }
    PgFont* f = &PG_FONTS[PG_FONTS_N];
    f->glyphs = malloc(65536 * sizeof(PgGlyph));
    for (int i=0; i<65536; i++) {
        f->glyphs[i].img = -1;
    }
    f->size = size;
    f->char_spacing = cs;
    f->vertical_spacing = size * vs;
    return PG_FONTS_N++;
}

static void pg_font_glyph (int fi, int u, int img, int x1, int y1, int x2, int y2,
                           int ox, int oy, int adv) {
    if (fi<0 || fi>=PG_FONTS_N || u<0 || u>=65536) {
        return;
    }
    PgGlyph g = { x1, y1, x2-x1, y2-y1, ox, oy, adv, img };
    PG_FONTS[fi].glyphs[u] = g;
}

// The next unicode of an UTF-8 string, or -1 at the end.
static int pg_utf8 (const char** s) {
    const unsigned char* p = (const unsigned char*) *s;
    if (*p == 0) {
        return -1;
    }
    int c = *p++;
    int n = 0;
    if      (c >= 0xF0) { c &= 0x07; n = 3; }
    else if (c >= 0xE0) { c &= 0x0F; n = 2; }
    else if (c >= 0xC0) { c &= 0x1F; n = 1; }
    while (n-- > 0 && (*p & 0xC0) == 0x80) {
        c = (c << 6) | (*p++ & 0x3F);
    }
    *s = (const char*) p;
    return c;
}

// The width of the first line of `s`.
static int pg_font_line_width (int fi, const char* s) {
    PgFont* f = &PG_FONTS[fi];
    float w = 0;
    int u;
    while ((u = pg_utf8(&s)) > 0 && u != '\n') {
        if (u < 65536 && f->glyphs[u].img >= 0) {
            w += f->glyphs[u].adv + f->char_spacing;
        }
    }
    return (int) w;
}

static int pg_font_width (int fi, const char* s) {
    if (fi<0 || fi>=PG_FONTS_N || s==NULL) {
        return 0;
    }
    int w = 0;
    while (1) {
        int l = pg_font_line_width(fi, s);
        if (l > w) w = l;
        const char* nl = strchr(s, '\n');
        if (nl == NULL) break;
        s = nl + 1;
    }
    return w;
}

// Draws a text. The origin is 0 (left), 1 (center), or 2 (right) of
// the top of the text, as in the original.
static void pg_font_draw (int fi, const char* s, int x, int y, int origin, int alpha) {
    if (fi<0 || fi>=PG_FONTS_N || s==NULL || PG_REN==NULL) {
        return;
    }
    PgFont* f = &PG_FONTS[fi];
    float fy = y + f->size;
    while (1) {
        int lw = pg_font_line_width(fi, s);
        float dx = x - (origin==1 ? lw/2 : (origin==2 ? lw : 0));
        int u;
        while ((u = pg_utf8(&s)) > 0 && u != '\n') {
            if (u < 65536 && f->glyphs[u].img >= 0) {
                PgGlyph* g = &f->glyphs[u];
                if (g->w > 0 && g->h > 0)       // a space has no image
                pg_img_draw(g->img, g->x, g->y, g->w, g->h,
                            (int)dx + g->ox, (int)fy + g->oy, 0, 0, alpha);
                dx += g->adv + f->char_spacing;
            }
        }
        if (u != '\n') {
            break;
        }
        fy += f->vertical_spacing;
    }
}

///////////////////////////////////////////////////////////////////////////////
// SOUNDS AND MUSIC
///////////////////////////////////////////////////////////////////////////////

static double PG_SND_VOL;
static void pg_sound (const char* path, double volume) {
    static struct { char* path; Mix_Chunk* snd; } SNDS[64];
    static int N = 0;
    if (!PG_SND || path==NULL) {
        return;
    }
    Mix_Chunk* snd = NULL;
    for (int i=0; i<N; i++) {
        if (!strcmp(SNDS[i].path, path)) {
            snd = SNDS[i].snd;
        }
    }
    if (snd==NULL && N<64) {
        snd = Mix_LoadWAV(path);
        if (snd != NULL) {
            SNDS[N].path = strdup(path);
            SNDS[N].snd  = snd;
            N++;
        }
    }
    if (snd != NULL) {
        int ch = Mix_PlayChannel(-1, snd, 0);
        if (ch >= 0) {
            Mix_Volume(ch, (int)(volume * PG_SND_VOL * MIX_MAX_VOLUME));
        }
    }
}

// The volumes of the sounds and of the music, from 0 to 1.
static void pg_volume (double snd, double mus) {
    PG_SND_VOL = snd;
    if (PG_SND) {
        Mix_Volume(-1, (int)(snd * MIX_MAX_VOLUME));
        Mix_VolumeMusic((int)(mus * MIX_MAX_VOLUME));
    }
}

static double PG_SND_VOL = 1.0;

static Mix_Music* PG_MUS = NULL;
static char*      PG_MUS_PATH = NULL;

static void pg_music_stop (void) {
    if (PG_MUS != NULL) {
        Mix_HaltMusic();
        Mix_FreeMusic(PG_MUS);
        PG_MUS = NULL;
        free(PG_MUS_PATH);
        PG_MUS_PATH = NULL;
    }
}

static void pg_music (const char* path) {
    if (!PG_SND || path==NULL) {
        return;
    }
    if (PG_MUS_PATH != NULL && !strcmp(PG_MUS_PATH, path)) {
        return;     // already playing
    }
    pg_music_stop();
    PG_MUS = Mix_LoadMUS(path);
    if (PG_MUS != NULL) {
        PG_MUS_PATH = strdup(path);
        Mix_PlayMusic(PG_MUS, -1);
    }
}

///////////////////////////////////////////////////////////////////////////////
// GROUND: the collision map and the ground map of the level
///////////////////////////////////////////////////////////////////////////////

enum {
    GP_NOTHING, GP_SOLID, GP_TRANSPARENT, GP_GROUND, GP_BRIDGE,
    GP_WATER, GP_LAVA, GP_REMOVE, GP_OUTOFSCREEN
};

#define PG_TILE 128

typedef struct {
    int           w, h;
    uint8_t*      col;      // ground type per pixel
    SDL_Surface*  gfx;      // the image of the ground, RGBA32
    int           tw, th;   // number of tiles
    SDL_Texture** tiles;
    uint8_t*      dirty;
    unsigned      serial;   // changes of the collision map
    SDL_Texture*  small;    // the small map
    int           small_w, small_h;
    unsigned      small_serial;
} PgMap;

static PgMap PG_MAP;

static void pg_map_free (void) {
    PgMap* m = &PG_MAP;
    if (m->col == NULL) {
        return;
    }
    free(m->col);
    SDL_FreeSurface(m->gfx);
    for (int i=0; i<m->tw*m->th; i++) {
        if (m->tiles[i] != NULL) {
            SDL_DestroyTexture(m->tiles[i]);
        }
    }
    free(m->tiles);
    free(m->dirty);
    if (m->small != NULL) {
        SDL_DestroyTexture(m->small);
    }
    memset(m, 0, sizeof(PgMap));
}

static void pg_map_new (int w, int h) {
    pg_map_free();
    PgMap* m = &PG_MAP;
    m->w = w;
    m->h = h;
    m->col = calloc(w*h, 1);
    m->gfx = SDL_CreateRGBSurfaceWithFormat(0, w, h, 32, SDL_PIXELFORMAT_RGBA32);
    SDL_FillRect(m->gfx, NULL, 0);
    m->tw = (w + PG_TILE - 1) / PG_TILE;
    m->th = (h + PG_TILE - 1) / PG_TILE;
    m->tiles = calloc(m->tw*m->th, sizeof(SDL_Texture*));
    m->dirty = calloc(m->tw*m->th, 1);
}

static int pg_map_get (int x, int y) {
    PgMap* m = &PG_MAP;
    if (x>=0 && x<m->w && y>=0 && y<m->h) {
        return m->col[y*m->w + x];
    }
    return GP_OUTOFSCREEN;
}

static void pg_map_dirty (int x, int y, int w, int h) {
    PgMap* m = &PG_MAP;
    int x1 = x < 0 ? 0 : x / PG_TILE;
    int y1 = y < 0 ? 0 : y / PG_TILE;
    int x2 = (x + w) / PG_TILE;
    int y2 = (y + h) / PG_TILE;
    for (int ty=y1; ty<=y2 && ty<m->th; ty++) {
        for (int tx=x1; tx<=x2 && tx<m->tw; tx++) {
            m->dirty[ty*m->tw + tx] = 1;
        }
    }
}

// Puts an image in the ground map, and its opaque pixels in the
// collision map with the given type.
static void pg_map_put (int i, int x0, int y0, int type) {
    PgMap* m = &PG_MAP;
    PgImg* img = pg_img(i);
    if (img==NULL || m->col==NULL) {
        return;
    }
    SDL_Rect r = { x0, y0, img->w, img->h };
    SDL_BlitSurface(img->sfc, NULL, m->gfx, &r);
    pg_map_dirty(x0, y0, img->w, img->h);
    if (type == GP_TRANSPARENT) {
        return;     // only drawn, as in the original
    }
    m->serial++;
    uint8_t* src = img->sfc->pixels;
    int pitch = img->sfc->pitch;
    for (int y=0; y<img->h; y++) {
        int yy = y + y0;
        if (yy<0 || yy>=m->h) continue;
        for (int x=0; x<img->w; x++) {
            int xx = x + x0;
            if (xx<0 || xx>=m->w) continue;
            if (src[y*pitch + 4*x + 3] != 255) continue;
            uint8_t* p = &m->col[yy*m->w + xx];
            if (type!=GP_BRIDGE || *p==GP_NOTHING) {
                *p = type;
            }
        }
    }
}

// Removes from the ground map the opaque pixels of `gi`, and from the
// collision map those of `ci`, except where the ground is solid.
static void pg_map_remove (int gi, int ci, int x0, int y0) {
    PgMap* m = &PG_MAP;
    PgImg* g = pg_img(gi);
    PgImg* c = pg_img(ci);
    if (g==NULL || c==NULL || m->col==NULL) {
        return;
    }
    uint8_t* dst = m->gfx->pixels;
    int dpitch = m->gfx->pitch;
    uint8_t* src = g->sfc->pixels;
    int spitch = g->sfc->pitch;
    for (int y=0; y<g->h; y++) {
        int yy = y + y0;
        if (yy<0 || yy>=m->h) continue;
        for (int x=0; x<g->w; x++) {
            int xx = x + x0;
            if (xx<0 || xx>=m->w) continue;
            if (src[y*spitch + 4*x + 3]==255 && m->col[yy*m->w+xx]!=GP_SOLID) {
                dst[yy*dpitch + 4*xx + 3] = 0;
            }
        }
    }
    pg_map_dirty(x0, y0, g->w, g->h);
    m->serial++;
    src = c->sfc->pixels;
    spitch = c->sfc->pitch;
    for (int y=0; y<c->h; y++) {
        int yy = y + y0;
        if (yy<0 || yy>=m->h) continue;
        for (int x=0; x<c->w; x++) {
            int xx = x + x0;
            if (xx<0 || xx>=m->w) continue;
            if (src[y*spitch + 4*x + 3] == 255) {
                uint8_t* p = &m->col[yy*m->w + xx];
                if (*p != GP_SOLID) {
                    *p = GP_NOTHING;
                }
            }
        }
    }
}

// Draws the ground map, with the level at `ox,oy` of the screen.
static void pg_map_draw (int ox, int oy) {
    PgMap* m = &PG_MAP;
    if (m->col==NULL || PG_REN==NULL) {
        return;
    }
    for (int ty=0; ty<m->th; ty++) {
        int y = ty*PG_TILE + oy;
        if (y >= PG_H || y+PG_TILE <= 0) continue;
        for (int tx=0; tx<m->tw; tx++) {
            int x = tx*PG_TILE + ox;
            if (x >= PG_W || x+PG_TILE <= 0) continue;
            int k = ty*m->tw + tx;
            int w = (tx==m->tw-1) ? m->w - tx*PG_TILE : PG_TILE;
            int h = (ty==m->th-1) ? m->h - ty*PG_TILE : PG_TILE;
            if (m->tiles[k] == NULL) {
                m->tiles[k] = SDL_CreateTexture(PG_REN, SDL_PIXELFORMAT_RGBA32,
                                SDL_TEXTUREACCESS_STREAMING, w, h);
                SDL_SetTextureBlendMode(m->tiles[k], SDL_BLENDMODE_BLEND);
                m->dirty[k] = 1;
            }
            if (m->dirty[k]) {
                uint8_t* p = (uint8_t*)m->gfx->pixels
                           + ty*PG_TILE*m->gfx->pitch + tx*PG_TILE*4;
                SDL_UpdateTexture(m->tiles[k], NULL, p, m->gfx->pitch);
                m->dirty[k] = 0;
            }
            SDL_Rect d = { x, y, w, h };
            SDL_RenderCopy(PG_REN, m->tiles[k], NULL, &d);
        }
    }
}

// Draws the small map at `x,y` with size `w x h`. It is rebuilt only
// when the collision map changes.
static void pg_map_small (int x, int y, int w, int h) {
    PgMap* m = &PG_MAP;
    if (m->col==NULL || PG_REN==NULL || w<=0 || h<=0) {
        return;
    }
    if (m->small==NULL || m->small_w!=w || m->small_h!=h) {
        if (m->small != NULL) {
            SDL_DestroyTexture(m->small);
        }
        m->small = SDL_CreateTexture(PG_REN, SDL_PIXELFORMAT_RGBA32,
                        SDL_TEXTUREACCESS_STREAMING, w, h);
        SDL_SetTextureBlendMode(m->small, SDL_BLENDMODE_BLEND);
        m->small_w = w;
        m->small_h = h;
        m->small_serial = m->serial - 1;
    }
    if (m->small_serial != m->serial) {
        m->small_serial = m->serial;
        uint32_t* px = malloc(w*h*4);
        for (int sy=0; sy<h; sy++) {
            for (int sx=0; sx<w; sx++) {
                int cx = sx * m->w / w;
                int cy = sy * m->h / h;
                uint8_t r=0, g=0, b=0, a=255;
                switch (m->col[cy*m->w + cx]) {
                    case GP_NOTHING:                         a = 200;        break;
                    case GP_SOLID:  r=100; g=100; b=125;                     break;
                    case GP_BRIDGE: r=0;   g=255; b=100;                     break;
                    case GP_WATER:
                    case GP_LAVA:   r=0;   g=0;   b=200;                     break;
                    default:        r=200; g=200; b=200;                     break;
                }
                uint8_t* q = (uint8_t*) &px[sy*w + sx];
                q[0]=r; q[1]=g; q[2]=b; q[3]=a;
            }
        }
        SDL_UpdateTexture(m->small, NULL, px, w*4);
        free(px);
    }
    SDL_Rect d = { x, y, w, h };
    SDL_RenderCopy(PG_REN, m->small, NULL, &d);
}

///////////////////////////////////////////////////////////////////////////////
// DRIVER
///////////////////////////////////////////////////////////////////////////////

static AVal pg_field (AVal t, const char* k, AVal v) {
    AVal key = a_strz(k);
    a_setindex(t, key, v);
    a_dec(key);
    a_dec(v);
    return t;
}

// Emits `:tag`, or `:tag [name=...]`, or `:tag [x=,y=,but=]`.
static AStatus pg_emit (const char* tag, const char* name, int x, int y, int but) {
    AVal t = a_strz(tag);
    AVal evt = a_tab();
    a_tag(evt, t);
    if (name != NULL) {
        pg_field(evt, "name", a_strz(name));
    } else {
        pg_field(evt, "x", a_int(x));
        pg_field(evt, "y", a_int(y));
        pg_field(evt, "but", a_int(but));
    }
    AStatus st = atm_emit(evt);
    a_dec(evt);
    a_dec(t);
    return st;
}

static void pg_shot (const char* path) {
    int w, h;
    SDL_GetRendererOutputSize(PG_REN, &w, &h);
    SDL_Surface* sfc = SDL_CreateRGBSurfaceWithFormat(0, w, h, 32, SDL_PIXELFORMAT_RGBA32);
    SDL_RenderReadPixels(PG_REN, NULL, SDL_PIXELFORMAT_RGBA32, sfc->pixels, sfc->pitch);
    IMG_SavePNG(sfc, path);
    SDL_FreeSurface(sfc);
}

// The test script: the entries `frame:...` of a variable that are due.
//
//   PINGUS_KEYS   = f:dn:Name,f:up:Name,...
//   PINGUS_MOUSE  = f:mv:x:y,f:dn:x:y:b,f:up:x:y:b,...
//   PINGUS_SHOT   = f:path.png,...
static AStatus pg_script (const char* var, int frame) {
    AStatus st = A_OK;
    const char* s = getenv(var);
    while (s!=NULL && *s!='\0' && st==A_OK) {
        char item[256];
        size_t n = strcspn(s, ",");
        snprintf(item, sizeof(item), "%.*s", (int)n, s);
        s += n + (s[n] == ',');
        char* arg = strchr(item, ':');
        if (arg==NULL || atoi(item)!=frame) {
            continue;
        }
        arg++;
        if (!strcmp(var, "PINGUS_SHOT")) {
            pg_shot(arg);
        } else if (!strcmp(var, "PINGUS_KEYS")) {
            if (!strncmp(arg, "dn:", 3)) {
                st = pg_emit("sdl.key.dn", arg+3, 0, 0, 0);
            } else if (!strncmp(arg, "up:", 3)) {
                st = pg_emit("sdl.key.up", arg+3, 0, 0, 0);
            }
        } else {
            int x=0, y=0, b=1;
            sscanf(arg+3, "%d:%d:%d", &x, &y, &b);
            if (!strncmp(arg, "mv:", 3)) {
                st = pg_emit("sdl.mouse.motion", NULL, x, y, 0);
            } else if (!strncmp(arg, "dn:", 3)) {
                st = pg_emit("sdl.mouse.motion", NULL, x, y, 0);
                if (st == A_OK) st = pg_emit("sdl.mouse.dn", NULL, x, y, b);
            } else if (!strncmp(arg, "up:", 3)) {
                st = pg_emit("sdl.mouse.up", NULL, x, y, b);
            }
        }
    }
    return st;
}

static int PG_FRAME = 0;

int main (int argc, char** argv) {
    if (SDL_Init(SDL_INIT_VIDEO|SDL_INIT_AUDIO) != 0) {
        SDL_Init(SDL_INIT_VIDEO);
    }
    PG_SND = getenv("PINGUS_MUTE")==NULL &&
             (Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 1024) == 0);
    if (PG_SND) {
        Mix_AllocateChannels(32);
    }

    // test mode: a fixed number of frames with a fixed duration
    int frames = -1;
    int fixed  = 0;
    if (getenv("PINGUS_FRAMES") != NULL) {
        sscanf(getenv("PINGUS_FRAMES"), "%d:%d", &frames, &fixed);
        PG_TEST = 1;
    }
    // frame rate: 40 frames per second, as the original
    int fps = 40;
    if (getenv("PINGUS_FPS") != NULL) {
        fps = atoi(getenv("PINGUS_FPS"));
    }
    int period = (fps > 0) ? 1000/fps : 0;

    PG_WIN = SDL_CreateWindow("Pingus", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              PG_W, PG_H, 0);
    if (PG_WIN != NULL) {
        PG_REN = SDL_CreateRenderer(PG_WIN, -1, 0);
    }
    if (PG_REN == NULL) {
        fprintf(stderr, "sdl : %s\n", SDL_GetError());
        exit(1);
    }

    atm_init(argc, argv);
    AStatus st = atm_main();

    Uint32 prv = SDL_GetTicks();
    int quit = 0;
    for (int frame=1; st==A_OK && !quit && atm_alive(); frame++) {
        PG_FRAME = frame;
        Uint32 t0 = SDL_GetTicks();
        SDL_Event e;
        while (st==A_OK && SDL_PollEvent(&e)) {
            switch (e.type) {
                case SDL_QUIT:
                    st = pg_emit("sdl.quit", "", 0, 0, 0);
                    quit = 1;
                    break;
                case SDL_KEYDOWN:
                    if (!e.key.repeat) {
                        st = pg_emit("sdl.key.dn", SDL_GetKeyName(e.key.keysym.sym), 0, 0, 0);
                    }
                    break;
                case SDL_KEYUP:
                    st = pg_emit("sdl.key.up", SDL_GetKeyName(e.key.keysym.sym), 0, 0, 0);
                    break;
                case SDL_MOUSEMOTION:
                    st = pg_emit("sdl.mouse.motion", NULL, e.motion.x, e.motion.y, 0);
                    break;
                case SDL_MOUSEBUTTONDOWN:
                    st = pg_emit("sdl.mouse.dn", NULL, e.button.x, e.button.y, e.button.button);
                    break;
                case SDL_MOUSEBUTTONUP:
                    st = pg_emit("sdl.mouse.up", NULL, e.button.x, e.button.y, e.button.button);
                    break;
            }
        }
        if (st == A_OK) st = pg_script("PINGUS_KEYS",  frame);
        if (st == A_OK) st = pg_script("PINGUS_MOUSE", frame);

        // time
        Uint32 now = SDL_GetTicks();
        int ms = fixed ? fixed : (int)(now - prv);
        prv = now;
        if (st==A_OK && ms>0) {
            st = atm_emit(a_int((int64_t)ms * 1000));
        }

        // screen
        if (st == A_OK) {
            SDL_SetRenderDrawColor(PG_REN, 0, 0, 0, 255);
            SDL_RenderClear(PG_REN);
            st = pg_emit("sdl.draw", "", 0, 0, 0);
            pg_script("PINGUS_SHOT", frame);
            SDL_RenderPresent(PG_REN);
        }

        if (frames>0 && frame>=frames) {
            quit = 1;
        } else if (!fixed && period>0) {
            int spent = (int)(SDL_GetTicks() - t0);
            if (spent < period) {
                SDL_Delay(period - spent);
            }
        }
    }

    if (getenv("PINGUS_COUNT") != NULL) {
        fprintf(stderr, "frames: %d\n", PG_FRAME);
    }
    if (st == A_OK) {
        st = atm_stop();
    }
    fflush(stdout);
    if (st == A_ESCAPE) {
        st = a_escape_err();
    }
    if (st != A_OK) {
        a_error_dump();
    }
    atm_quit();
    pg_map_free();
    pg_music_stop();
    if (PG_SND) {
        Mix_CloseAudio();
    }
    SDL_Quit();
    return (st == A_OK) ? 0 : 1;
}

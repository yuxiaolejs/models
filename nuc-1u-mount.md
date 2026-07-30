# 1U rack mount — Intel NUC 11 slim

Forked from `rack-panel.FCStd`. That file is untouched.

- `nuc-1u-mount.py` — parametric source, the thing to edit
- `nuc-1u-mount.FCStd` — generated model
- `export/` — STEP + STL, orthographic views, build & verify reports

Regenerate after any edit:

```
/home/unics/Downloads/FreeCAD_1.1.1-Linux-x86_64-py311.AppImage \
    --console nuc-1u-mount.py < /dev/null
```

The generated `.FCStd` and everything in `export/` are gitignored — they rebuild
exactly from the .py, which has no nondeterminism in it. To pin the STL you
actually sent to the printer for some revision, `git add -f` it.

## Revisions

- **v1** — first printed and test-fitted. M3 spacing confirmed at 85 mm; holes
  were on the wrong axis, then rotated to fore/aft at y = 21 / 106.
- **v2** — NUC moved 2 mm forward (port recess 7.5 → 5.5), tail shortened from
  y = 123.5 to y = 112, rear stops deleted because they fouled the HDMI and DC
  connectors. Mount holes follow the NUC to y = 19 / 104.

## Mounting screws

85 mm centre distance, **confirmed on the printed part**, on a **fore/aft axis**:
the two slots sit on the tray centreline, one ahead of and one behind the
airflow grid. Read back off the solid:

| | x | y |
|---|---|---|
| front slot | 140.0 (centre), 128–152 travel | **19.0** |
| rear slot | 140.0 (centre), 128–152 travel | **104.0** |

Spacing measured on the geometry: 85.000 mm along Y, 0.000 mm along X. (These
moved 2 mm forward in v2 along with the NUC — on v1 they were at 21.0 and 106.0.)

Each slot is elongated 24 mm **across** the rack, since the fore/aft spacing is
the known quantity and the transverse position is the one with slack. If the
pair turns out not to be centred on the NUC's depth, set `M3_OFFSET_Y` in the .py
to shift both together — the spacing stays locked at `M3_SPACING`.

## Parts

| | size | notes |
|---|---|---|
| `PartA_NUC_tray` | 251.0 × 114.0 × 43.6 | left half + NUC cradle, 72 cm³ |
| `PartB_filler` | 251.0 × 43.6 × 5.0 | right half, vented blank, 39 cm³ |
| `TestCoupon_M3` | 58 × 119 × 12 | throwaway hole-pattern gauge |

Both halves are 251.0 mm — same as your original split, so they fit the same bed.

## Rack geometry (corrected against EIA-310)

| | this model | your `rack-panel` |
|---|---|---|
| panel width | 482.60 | 482.00 |
| panel height | 43.60 | 44.00 (0.34 over spec) |
| ear spacing | 465.10 | 465.10 whole / **466.0 mirrored** |
| ear V spacing | 31.75 | 31.75 |
| slot | Ø6.6 × 10.6 obround | Ø7.2 × 11.2 obround |
| lap clearance | 0.20 | 0.00 (press fit) |

Ear slots are now symmetric about the panel centreline, so mirroring a half
gives the right answer instead of drifting 0.9 mm wide.

## Printing

Both parts are already oriented in the STLs — **do not rotate them**.

- Part A prints tray-down, panel standing up. No supports needed: the
  countersinks open downward at 45°, everything else is vertical wall.
- Part B prints lying flat on its face.
- PETG or ASA preferred over PLA — a rack gets warm and PLA creeps under
  sustained load. 4 perimeters, ≥40 % infill in part A's floor.
- The panel is only 5 mm thick and prints as a vertical wall, so layer adhesion
  is what holds the rack ears on. Don't print it cold or fast.

## Hardware

- 4 × M6 (or 10-32) cage nuts + screws — rack ears
- 3 × M6 × 20 + nuts — half-lap joint at x = 241.3
- 2 × **M3 countersunk** (flat head, 90°) — NUC to tray. Flat head matters:
  the floor is 2.8 mm and the head must sit flush or it fouls the U below.
  Length depends on how deep the NUC's threads are; 8 mm is a sensible start.

## Fit and clearances

- NUC pocket 118.2 mm wide, 0.6 mm per side on a 117 mm chassis
- NUC sits z = 2.8 → 39.8, panel top at 43.6, so **3.8 mm of air above it**
- Front face sits **5.5 mm** behind the panel front — the panel thickness plus
  0.5 mm of clearance, nothing more. Measured masking of the chassis front face
  through the window: **0.00 %**.
- **Nothing behind the tray.** The floor stops at y = 112, which is 5 mm of solid
  material behind the rear countersink and **5.5 mm ahead of the NUC's own rear
  face**. The rear stops are gone. Verified by intersecting a 60 mm deep box
  spanning the full rack behind y = 112: zero material.
- Verified by boolean intersection: zero collision between the chassis body and
  part A, zero interference between the two halves, nothing outside the 1U
  envelope, nothing below z = 0.

**Keep the rubber feet on.** Two reasons now. The NUC 11 draws intake air through
its base, and the feet hold it 3 mm off the floor over the cut-open plenum — and
the junction haunch runs *under* the front lip of the chassis, in that same 3 mm
gap. `NUC_FOOT_H = 3.0` in the .py is the assumption; the haunch is only 1.5 mm
tall across the pocket, so there's 1.5 mm of margin if your feet are shorter than
I think. Take the feet off and the NUC will sit on the haunch.

## Panel-to-tray reinforcement

Three things tie the vertical panel to the horizontal tray, all at 45° so none
of them need support material:

1. **Haunch** — a 45° fillet along the entire panel/floor junction. 2.5 mm tall
   outboard of the NUC where it has room, dropping to 1.5 mm across the pocket
   so it tucks under the chassis in the gap the rubber feet leave. Kills the
   sharp inside corner, which is where a printed part in this shape cracks.
2. **Corner webs** — 9 mm thick, 28 mm tall triangular gussets outboard of the
   NUC on both sides, from the panel back face down to the floor.
3. **Side walls** — continuous 14 mm walls running the full depth, so the tray is
   a channel section rather than a flat plate. Each is pierced by three 12 × 7
   slots so air can still cross.

Section properties measured off the solid (not estimated), against a bare
2.8 × 136.2 plate as reference, 504 g acting at the NUC's mid-depth, PETG at
E = 2 GPa:

| section | I (mm⁴) | vs. bare plate | tip sag |
|---|---|---|---|
| bare plate | 249 | 1× | 1.41 mm |
| y = 8 (in the webs) | 63 570 | 255× | 0.006 mm |
| y = 25 | 8 191 | 33× | 0.043 mm |
| y = 61.5 (mid-span) | 6 478 | 26× | 0.054 mm |
| y = 108 (rear) | 6 478 | 26× | 0.054 mm |

~0.05 mm of sag across the whole tray, before the NUC is even bolted down.

## Known soft spots

- 2.6 mm of material outboard of the rack slots vertically. That's inherent to
  the standard — real steel panels are the same — but it's the first thing that
  will crack if you overtighten the rack screws.
- Part A carries all the weight on one ear pair, ~140 mm from the left rail.
  Load is only ~5 N so it's not a concern, but do bolt the half-lap joint.
- The top of the NUC window is a 118 mm horizontal bridge in a vertical wall.
  It'll print, but turn on your slicer's bridge settings and don't run the fan
  low — a sagging first bridge layer is the one cosmetic risk on part A.

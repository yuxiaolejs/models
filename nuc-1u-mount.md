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

## Mounting screws

85 mm centre distance, **confirmed on the printed part**, on a **fore/aft axis**:
the two slots sit on the tray centreline, one ahead of and one behind the
airflow grid. Read back off the solid:

| | x | y |
|---|---|---|
| front slot | 140.0 (centre), 128–152 travel | **21.0** |
| rear slot | 140.0 (centre), 128–152 travel | **106.0** |

Spacing measured on the geometry: 85.000 mm along Y, 0.000 mm along X.

Each slot is elongated 24 mm **across** the rack now, since the fore/aft spacing
is the known quantity and the transverse position is the one with slack. If the
pair turns out not to be centred on the NUC's depth, set `M3_OFFSET_Y` in the .py
to shift both together — the spacing stays locked at `M3_SPACING`.

### Salvaging the part you already printed

You don't have to reprint. On the old part the floor is solid at both new
locations (the previous openings ran y 30.5–62.5 and 68.5–100.5, and x 140 is the
central rib), so you can just drill it:

- two Ø3.4 holes on the tray centreline — i.e. midway across the floor
- **21.0 mm and 106.0 mm** back from the panel's front face, or equivalently
  **102.5 mm and 17.5 mm** forward from the rear edge of the tray floor
- countersink from underneath with a 6 mm bit, 1.3 mm deep, so the flat head
  finishes flush with the 2.8 mm floor

The two old slots stay as spare holes — harmless, and handy for cable ties.

## Parts

| | size | notes |
|---|---|---|
| `PartA_NUC_tray` | 251.0 × 125.5 × 43.6 | left half + NUC cradle, 80 cm³ |
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
- Front face sits 7.5 mm behind the panel front (5 mm panel + 2.5 mm haunch) and
  is exposed through a 118.2 × 37.2 window. Only the bottom 0.05 % of the face
  is masked, by the haunch. Power button and both USB-A are clear; a USB plug
  reaches into a 7.5 mm recess without trouble.
- Verified by boolean intersection: zero collision between the NUC envelope and
  part A, zero interference between the two halves, nothing outside the 1U
  envelope, nothing below z = 0.

**Keep the rubber feet on.** The NUC 11 draws intake air through its base; the
feet hold it 3 mm off the tray floor and the floor is cut open underneath. Take
them off and you close the plenum.

## Panel-to-tray reinforcement

Three things tie the vertical panel to the horizontal tray, all at 45° so none
of them need support material:

1. **Haunch** — a 2.5 mm fillet running the entire length of the panel/floor
   junction, full tray width. Kills the sharp inside corner, which is where a
   printed part in this shape actually cracks.
2. **Corner webs** — 9 mm thick, 28 mm tall triangular gussets outboard of the
   NUC on both sides, from the panel back face down to the floor.
3. **Side walls** — the old 7 mm rail segments are now continuous 14 mm walls
   running the full depth, so the tray is a channel section instead of a flat
   plate. Each is pierced by three 12 × 7 slots so air can still cross.

Section properties measured off the solid (not estimated), against a bare
2.8 × 136.2 plate as reference, 504 g acting at the NUC's mid-depth, PETG at
E = 2 GPa:

| section | I (mm⁴) | vs. bare plate | tip sag |
|---|---|---|---|
| bare plate | 249 | 1× | 1.47 mm |
| y = 10 (in the webs) | 51 500 | 207× | 0.007 mm |
| y = 25 | 8 190 | 33× | 0.045 mm |
| y = 63 (mid-span) | 6 398 | 26× | 0.057 mm |
| y = 115 (rear) | 6 478 | 26× | 0.056 mm |

So ~0.06 mm of sag across the whole tray, before the NUC is even bolted down.
Cost: +15 cm³ of filament and 2.5 mm more port recess.

## Known soft spots

- 2.6 mm of material outboard of the rack slots vertically. That's inherent to
  the standard — real steel panels are the same — but it's the first thing that
  will crack if you overtighten the rack screws.
- Part A carries all the weight on one ear pair, ~140 mm from the left rail.
  Load is only ~5 N so it's not a concern, but do bolt the half-lap joint.
- The top of the NUC window is a 118 mm horizontal bridge in a vertical wall.
  It'll print, but turn on your slicer's bridge settings and don't run the fan
  low — a sagging first bridge layer is the one cosmetic risk on part A.

# 1U rack conversion — MOTU M2

Forked from `nuc-1u-mount.py`. Same EIA-310 panel, same half-lap split, same
part B filler.

- `motu-m2-1u-mount.py` — parametric source, the thing to edit
- `motu-m2-1u-mount.FCStd` — generated model (gitignored)
- `export/motu-m2/` — STEP + STL, `build-report.txt`

Regenerate after any edit:

```
/home/unics/Downloads/FreeCAD_1.1.1-Linux-x86_64-py311.AppImage \
    --console motu-m2-1u-mount.py < /dev/null
```

## Why the shell has to go

The stock aluminum shell is 44.73 mm tall outside (body measured 44.42). 1U is
44.45 mm pitch and 43.66 mm max equipment height, so the stock unit cannot go in
1U on any tray. The M2's front and rear plates are only 40 mm, and the internal
parts clear 38.6 mm, so with the shell replaced by a thinner printed one it fits.

## How it holds together (copied from stock)

Front plate + PCB + rear plate screw together into one rigid spool; the PCB is
the strut. Each end of the shell has a rebate the plate seats in, with a lip
behind it, so the shell is trapped between the plates. Nothing touches the PCB.

Here the **front rebate is cut into the rack panel**, so the MOTU front plate sits
flush in the rack face. The rear rebate is at the end of a tube cantilevered
off the panel back.

| | stock | this model |
|---|---|---|
| plate (W × H, R) | 185.6 × 40, R9 | rebate 186.0 × 40.4, R9.2 (0.2 fit) |
| lip, sides / top+bottom | 1.0 / 0.65 | 1.0 / 0.65 |
| cavity behind the lip | 183.6 × 38.73 | 183.6 × 38.7 |
| lip to lip (`SPAN`) | 103.5 | 103.5 |
| wall at the rebates, top/bottom | 2.0 | **1.6** |
| wall at the cavity, top/bottom | 3.0 | **2.45** |
| skin at the rebates, sides | 2.0 | 2.0 |
| outside height | 44.73 | **43.60** |

Verified by boolean on a stand-in of the M2 (plates + 38.6 mm parts envelope):
zero collision with part A, both plates bear on the lip over 304 mm² each,
part A entirely inside z = 0 … 43.6.

## PCB screws

Four screws up through the shell floor into the PCB standoffs (where the stock
feet screwed on). Best-effort measurement off the stock shell:

| | value |
|---|---|
| spacing, across × fore/aft | 125.0 × 31.5 c2c |
| front row | y = 38.75 (measured 38.5 from the front edge) |
| rear row | y = 70.25 (measured 37.5 from the rear edge) |
| across | centered on the M2 — "32.5-ish" each side, assumed |

The two edge readings disagree by 0.5 mm against the 108 shell, so the pattern
is centered between them. Holes are Ø3.6 slots with 2 mm of travel across the
rack (the least certain axis) and a swept 90° countersink, so an **M3 flat head**
sits flush and nothing hangs into the U below; 1.25 mm of floor is left under
the head. Screw diameter measured at 3 mm, so M3 is confirmed; length still
to pick — floor 2.45 + whatever the standoff thread depth allows.

## Assumptions to check

- **`PLATE_T = 2.25`** is derived, not measured: (108 outer − 103.5 lip-to-lip) / 2,
  i.e. the plates sit flush with the shell ends. Measure a plate. If it's off, the
  front plate sits proud of or recessed into the rack face; the fit is unaffected.
- **`SPAN = 103.5`** is the number that matters. Too long and the spool rattles;
  too short and the rear plate won't reach the PCB. `SPAN_ADJ` trims it without
  touching the measurement: positive for slack, negative for preload (stock is
  tight — the screws pull the plates hard onto the lips).

## Print the coupon first

`TestCoupon_shell` is the shell alone: both rebates, the full lip-to-lip
distance, joined by four corner longerons. ~52 cm³. Build the spool into it the
way it'll go into part A and check:

1. both plates drop into their rebates without forcing,
2. with the rear screws snug, the spool doesn't rattle fore/aft,
3. the rear plate actually pulls down onto the PCB rather than stalling on the lip,
4. all four bottom screws find their standoffs. The coupon keeps a floor strip
   under each column of screws for exactly this.

Adjust `SPAN_ADJ` (and `PLATE_FIT` if the rebates are tight), regenerate, and only
then print part A.

## Parts

| | size | notes |
|---|---|---|
| `PartA_M2_shell` | 251.0 × 108.0 × 43.6 | left half + shell, 140 cm³ |
| `PartB_filler` | 251.0 × 5.0 × 43.6 | right half, vented blank, 39 cm³ |
| `TestCoupon_shell` | 190.0 × 108.0 × 43.6 | fit gauge, 52 cm³ |

The M2 sits at x = 123.3 across the panel, wholly inside part A, clear of the
left rack ear and of the half-lap.

## Printing

All STLs are already oriented — **do not rotate them**.

- Part A and the coupon print **face-down**: panel flat on the bed, tube standing
  108 mm up. The front lip is then a 1 mm ledge over the rebate and the rear
  rebate just widens, so nothing bridges and no supports are needed. The rack
  ears print flat, which is much stronger than part A of the NUC mount.
- The tube's layer lines run around it, so the cantilever load pulls across
  layers. It's a closed box section carrying < 0.6 kg, so it's fine, but print
  PETG/ASA warm, 4 perimeters.
- The side webs are 45° and print unsupported.

## Assembly

1. Unscrew the rear plate from the PCB. Leave the front plate on.
2. Slide front plate + PCB in through the rack window until the front plate seats.
3. Fit the rear plate into the rear rebate and screw it back onto the PCB.
4. Four M3 flat heads up through the floor into the PCB standoffs. Snug, not
   tight — they're going into plastic-backed standoffs over a 2.45 mm floor.

## Known soft spots / open items

- **Shielding and ground.** The aluminum shell was the enclosure shield and
  probably part of the chassis ground. The plates are still tied together through
  the PCB screws, but nothing surrounds the board now. If hum or buzz shows up,
  line the cavity with copper foil tape bonded to one plate screw.
- **Heat.** The shell was also the heatsink. Three 4 × 70 slots in each side wall
  (`SIDE_VENT`); add top vents if it runs warm.
- The 1.6 mm wall above and below each rebate is thin, but it's only the 2.25 mm
  deep rim and it's backed by the tube walls right behind it.
- Plug forces on the front XLRs go into the front lip, through the plate. That's
  the same load path as stock.

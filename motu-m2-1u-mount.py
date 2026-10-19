#!/usr/bin/env freecad-console
"""
1U rack conversion for a MOTU M2, forked from nuc-1u-mount.py.

The stock aluminum shell is too tall for 1U (44.73 outside, 44.42 measured
body).  It is replaced by a printed shell built into the rack panel; the M2's
own front and rear plates, and the PCB between them, are reused untouched.

How the stock unit holds together, and what this copies:
  - front plate + PCB + rear plate are screwed into one rigid "spool"; the PCB
    is the strut that fixes the plate spacing
  - each open end of the shell has a rebate the plate drops into, with a 1 mm
    lip behind it, so the shell is captured between the two plates
  - nothing in the shell touches the PCB -- no rails, no standoffs
Here the front rebate is cut into the rack panel itself, so the MOTU front
plate sits flush in the rack face, and the rear rebate is at the end of a tube
cantilevered off the panel back.

Assembly, same order as stock: unscrew the rear plate, slide front plate + PCB
in through the rack window until the front plate seats, screw the rear plate
back on from behind.

Regenerate with:
  /home/unics/Downloads/FreeCAD_1.1.1-Linux-x86_64-py311.AppImage \
      --console motu-m2-1u-mount.py < /dev/null

Axes:  X = across the rack, Y = depth (0 = panel front face), Z = up.
"""

import math
import os
import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector as V

OUT_DIR = "/home/unics/Desktop/3dmodels"
DOC_PATH = os.path.join(OUT_DIR, "motu-m2-1u-mount.FCStd")
EXPORT_DIR = os.path.join(OUT_DIR, "export", "motu-m2")

# ---------------------------------------------------------------- rack panel
PANEL_W = 482.60          # 19"
PANEL_H = 43.60           # 1U:  44.45*1 - 0.79
PANEL_T = 5.00

EAR_X = 8.75              # slot centre in from each panel edge -> 465.10 apart
SLOT_R = 3.30             # Ø6.6 obround, M6 / 10-32 clearance
SLOT_TRAVEL = 4.00        # -> 10.6 x 6.6 obround
SLOT_DZ = 15.875          # +/- from panel centre (0.625")

# ------------------------------------------------------------- printable split
BED = 256.0
LAP = 19.40               # half-lap overlap; sized so both halves land on 251.0
LAP_GAP = 0.20            # total clearance across the lap
SPLIT_C = PANEL_W / 2.0   # 241.30
LAP_X0 = SPLIT_C - LAP / 2.0
LAP_X1 = SPLIT_C + LAP / 2.0
LAP_FRONT_T = (PANEL_T - LAP_GAP) / 2.0   # 2.40
JOINT_HOLE_R = 3.00                        # Ø6, matches the original
JOINT_HOLE_Z = (7.00, PANEL_H / 2.0, PANEL_H - 7.00)

# ------------------------------------------------- the M2, measured on the unit
PLATE_W = 185.60          # front / rear aluminum plates (same size)
PLATE_H = 40.00
PLATE_R = 9.00            # corner radius
PLATE_T = 2.25            # ASSUMED: (108 outer - 103.5 lip-to-lip) / 2, i.e.
                          # plates flush with the shell ends.  Calipers please.
LIP = 1.00                # stock step: how far the lip reaches in under the
                          # plate, at the sides
CAV_H = 38.70             # stock cavity height (44.73 - 2 x 3); measured
                          # internal parts clearance 38.6
CAV_R = 8.00              # cavity corner radius (plate R9 less the lip)
SPAN = 103.50             # lip to lip = PCB length.  THE critical number

# ------------------------------------------------------------- printed shell
PLATE_FIT = 0.20          # clearance per side, plate in its rebate
SPAN_ADJ = 0.00           # + gives axial slack, - gives preload: the stock unit
                          # is a hair short so the screws pull the plates hard
                          # onto the lips.  Tune on the coupon, not the big part
SKIN = 2.00               # outer skin at the sides of the rebates (stock: 2)
TUBE_R = 3.00             # outside corner radius of the tube
M2_CX = 123.30            # where the M2 sits across the panel (inside part A)
GUSSET = 10.0             # 45 deg webs from panel back to the tube sides

# --- bottom screws, PCB to shell ------------------------------------------
# Four screws up through the shell floor into PCB standoffs (where the feet
# were).  Measured c2c 125 across x 31.5 fore/aft; edges 38.5 front / 37.5 rear
# of the 108 stock shell, so the pair is centred between the two readings.
# Across the rack it's "32.5-ish" each side, so the holes slot +/-1 in x.
PCB_SCREW_DX = 125.0
PCB_SCREW_DY = 31.5
PCB_SCREW_YC = (38.5 + (108.0 - 37.5)) / 2.0   # 54.5 from the front face
PCB_SCREW_TRAVEL = 2.0    # transverse slot length (x)
M3_CLEAR_R = 1.80         # Ø3.6, a little float for a best-effort pattern
M3_HEAD_R = 3.00          # Ø6.0 flat head, 90 deg
M3_CSK_DEPTH = M3_HEAD_R - M3_CLEAR_R   # full cone, 1.2: head sits flush

SIDE_VENT = (4.0, 70.0)   # z x y slot in each tube side wall; the aluminum
SIDE_VENT_Z = (12.0, 21.8, 31.6)  # shell was the heatsink, PETG is not

# derived ------------------------------------------------------------------
CAV_W = PLATE_W - 2 * LIP                 # 183.6, opening behind the lip
REB_W = PLATE_W + 2 * PLATE_FIT           # 186.0
REB_H = PLATE_H + 2 * PLATE_FIT           # 40.4
REB_R = PLATE_R + PLATE_FIT

ZC = PANEL_H / 2.0
CAV_Z0 = ZC - CAV_H / 2.0                 # 2.45 of wall under the cavity
REB_Z0 = ZC - REB_H / 2.0                 # 1.60 of wall under the rebate

TUBE_W = REB_W + 2 * SKIN                 # 190.0
TUBE_X0 = M2_CX - TUBE_W / 2.0
TUBE_X1 = M2_CX + TUBE_W / 2.0

Y_LIP_F = PLATE_T                         # front plate seats here
Y_LIP_R = Y_LIP_F + SPAN + SPAN_ADJ       # rear plate seats here
Y_END = Y_LIP_R + PLATE_T                 # rear plate flush with the tube end

PCB_SCREW_X = (M2_CX - PCB_SCREW_DX / 2.0, M2_CX + PCB_SCREW_DX / 2.0)
PCB_SCREW_Y = (PCB_SCREW_YC - PCB_SCREW_DY / 2.0, PCB_SCREW_YC + PCB_SCREW_DY / 2.0)


# --------------------------------------------------------------------- helpers
def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))


def reduce_fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out


def rrect_y(xc, zc, w, h, r, y0, ylen):
    """Rounded rectangle in the XZ plane, extruded along +Y."""
    x0, z0 = xc - w / 2.0, zc - h / 2.0
    parts = [box(x0 + r, y0, z0, w - 2 * r, ylen, h),
             box(x0, y0, z0 + r, w, ylen, h - 2 * r)]
    for cx in (x0 + r, x0 + w - r):
        for cz in (z0 + r, z0 + h - r):
            parts.append(Part.makeCylinder(r, ylen, V(cx, y0, cz), V(0, 1, 0)))
    return reduce_fuse(parts).removeSplitter()


def slot_y(xc, zc, r, travel, y0, ylen):
    """Obround in the XZ plane, bored along +Y.  The rack ear slots."""
    a = Part.makeCylinder(r, ylen, V(xc - travel / 2.0, y0, zc), V(0, 1, 0))
    b = Part.makeCylinder(r, ylen, V(xc + travel / 2.0, y0, zc), V(0, 1, 0))
    m = box(xc - travel / 2.0, y0, zc - r, travel, ylen, 2 * r)
    return a.fuse(b).fuse(m)


def ear_slots(xc):
    """The two rack slots of one ear, as a single cutting solid."""
    lo = slot_y(xc, ZC - SLOT_DZ, SLOT_R, SLOT_TRAVEL, -2.0, PANEL_T + 4.0)
    hi = slot_y(xc, ZC + SLOT_DZ, SLOT_R, SLOT_TRAVEL, -2.0, PANEL_T + 4.0)
    return lo.fuse(hi)


def joint_holes():
    cuts = [Part.makeCylinder(JOINT_HOLE_R, PANEL_T + 4.0, V(SPLIT_C, -2.0, z), V(0, 1, 0))
            for z in JOINT_HOLE_Z]
    return reduce_fuse(cuts)


def vent_field(x0, x1, z0, z1, width=4.0, pitch=9.0):
    """Vertical slots through the panel, from x0 up to (not past) x1."""
    cuts = []
    x = x0
    while x + width <= x1:
        cuts.append(box(x, -2.0, z0, width, PANEL_T + 4.0, z1 - z0))
        x += pitch
    return cuts


def _axis(p0, p1):
    """Unit vector along the slot and the in-plane normal to it."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    return (dx, dy, L, -dy / L, dx / L)


def slot_z(p0, p1, r, z0, zlen):
    """Obround bored along +Z, elongated from (x,y) p0 to p1 in any direction."""
    dx, dy, _, nx, ny = _axis(p0, p1)
    a = Part.makeCylinder(r, zlen, V(p0[0], p0[1], z0), V(0, 0, 1))
    b = Part.makeCylinder(r, zlen, V(p1[0], p1[1], z0), V(0, 0, 1))
    pts = [V(p0[0] + nx * r, p0[1] + ny * r, z0),
           V(p1[0] + nx * r, p1[1] + ny * r, z0),
           V(p1[0] - nx * r, p1[1] - ny * r, z0),
           V(p0[0] - nx * r, p0[1] - ny * r, z0)]
    m = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, zlen))
    return a.fuse(b).fuse(m)


def csk_slot_z(p0, p1, r_big, r_small, depth, z0):
    """Swept 90 deg countersink for a slot, opening downwards at z0.

    A flat head seats flush anywhere along the slot, so nothing protrudes
    below the shell into the U underneath.
    """
    dx, dy, _, nx, ny = _axis(p0, p1)
    c0 = Part.makeCone(r_big, r_small, depth, V(p0[0], p0[1], z0), V(0, 0, 1))
    c1 = Part.makeCone(r_big, r_small, depth, V(p1[0], p1[1], z0), V(0, 0, 1))
    pts = [V(p0[0] + nx * r_big, p0[1] + ny * r_big, z0),
           V(p0[0] - nx * r_big, p0[1] - ny * r_big, z0),
           V(p0[0] - nx * r_small, p0[1] - ny * r_small, z0 + depth),
           V(p0[0] + nx * r_small, p0[1] + ny * r_small, z0 + depth)]
    prism = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(dx, dy, 0))
    return c0.fuse(c1).fuse(prism)


def pcb_screws():
    """Cutting solids for the four PCB screws through the shell floor."""
    out = []
    for x in PCB_SCREW_X:
        for y in PCB_SCREW_Y:
            p0 = (x - PCB_SCREW_TRAVEL / 2.0, y)
            p1 = (x + PCB_SCREW_TRAVEL / 2.0, y)
            out.append(slot_z(p0, p1, M3_CLEAR_R, -1.0, CAV_Z0 + 2.0))
            out.append(csk_slot_z(p0, p1, M3_HEAD_R, M3_CLEAR_R, M3_CSK_DEPTH, 0.0))
    return out


def side_web(x_wall, sign):
    """45 deg web from the panel back face to a tube side wall, full height.

    Printed face-down, the hypotenuse is a 45 deg overhang: no supports.
    """
    pts = [V(x_wall, PANEL_T, 0), V(x_wall + sign * GUSSET, PANEL_T, 0),
           V(x_wall, PANEL_T + GUSSET, 0)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, PANEL_H))


def tube_body(y0, y1):
    return rrect_y(M2_CX, ZC, TUBE_W, PANEL_H, TUBE_R, y0, y1 - y0)


def shell_cuts(y0, y1):
    """Front rebate, through cavity and rear rebate, spanning y0..y1."""
    return [
        rrect_y(M2_CX, ZC, REB_W, REB_H, REB_R, y0 - 1.0, Y_LIP_F - y0 + 1.0),
        rrect_y(M2_CX, ZC, CAV_W, CAV_H, CAV_R, y0 - 1.0, y1 - y0 + 2.0),
        rrect_y(M2_CX, ZC, REB_W, REB_H, REB_R, Y_LIP_R, y1 - Y_LIP_R + 1.0),
    ]


# ------------------------------------------------------------------- part A
def build_part_a():
    """Left half: 1U panel with the M2 shell built into it."""
    s = box(0, 0, 0, LAP_X1, PANEL_T, PANEL_H)
    # half-lap tongue: keep only the front leaf over the overlap
    s = s.cut(box(LAP_X0, LAP_FRONT_T, -1.0, LAP + 1.0, PANEL_T, PANEL_H + 2.0))

    s = s.fuse(tube_body(0.0, Y_END))
    s = s.fuse(side_web(TUBE_X0, -1))
    s = s.fuse(side_web(TUBE_X1, +1))

    cuts = shell_cuts(0.0, Y_END)
    cuts.append(ear_slots(EAR_X))
    cuts.append(joint_holes())
    cuts += pcb_screws()

    # vents through the tube side walls, clear of the webs and the rebates
    vz, vy = SIDE_VENT
    ymid = (Y_LIP_F + Y_LIP_R) / 2.0
    for x in (TUBE_X0 - 1.0, TUBE_X1 - (TUBE_W - CAV_W) / 2.0 - 1.0):
        for z in SIDE_VENT_Z:
            cuts.append(box(x, ymid - vy / 2.0, z - vz / 2.0,
                            (TUBE_W - CAV_W) / 2.0 + 2.0, vy, vz))

    return s.cut(reduce_fuse(cuts)).removeSplitter()


# ------------------------------------------------------------------- part B
def build_part_b():
    """Right half: plain vented 1U filler.  Identical to the NUC mount's."""
    s = box(LAP_X0, 0, 0, PANEL_W - LAP_X0, PANEL_T, PANEL_H)
    # half-lap: keep only the rear leaf over the overlap
    s = s.cut(box(LAP_X0 - 1.0, -1.0, -1.0,
                  LAP + 1.0, LAP_FRONT_T + LAP_GAP + 1.0, PANEL_H + 2.0))

    cuts = [ear_slots(PANEL_W - EAR_X), joint_holes()]
    cuts += vent_field(LAP_X1 + 10.0, PANEL_W - EAR_X - 20.0,
                       6.0, PANEL_H - 6.0, width=5.0, pitch=12.0)
    return s.cut(reduce_fuse(cuts))


# ------------------------------------------------------------- test coupon
def build_coupon():
    """The shell alone, skeletonized: both rebates joined by four corner
    longerons.  Checks plate fit and, above all, SPAN -- before committing to
    the full 250 mm part.
    """
    s = tube_body(0.0, Y_END).cut(reduce_fuse(shell_cuts(0.0, Y_END)))
    ya, yb = Y_LIP_F + 4.0, Y_LIP_R - 4.0
    keep = 14.0               # longeron size, measured from each corner
    strip = 14.0              # floor strips left under each PCB screw column
    windows = [
        # top wall
        box(TUBE_X0 + keep, ya, ZC, TUBE_W - 2 * keep, yb - ya, PANEL_H),
        # side walls
        box(TUBE_X0 - 1.0, ya, keep, TUBE_W + 2.0, yb - ya, PANEL_H - 2 * keep),
    ]
    # bottom wall: open, except a fore/aft strip under each column of screws
    xs = [TUBE_X0 + keep] + [e for x in PCB_SCREW_X
                             for e in (x - strip / 2.0, x + strip / 2.0)] + [TUBE_X1 - keep]
    for xa, xb in zip(xs[0::2], xs[1::2]):
        windows.append(box(xa, ya, -1.0, xb - xa, yb - ya, ZC + 1.0))
    s = s.cut(reduce_fuse(windows))
    return s.cut(reduce_fuse(pcb_screws())).removeSplitter()


# ------------------------------------------------------------- M2 stand-in
def build_spool():
    """Front plate + PCB envelope + rear plate, as installed.  Reference only:
    used to prove nothing printed touches the M2.
    """
    plate_f = rrect_y(M2_CX, ZC, PLATE_W, PLATE_H, PLATE_R, Y_LIP_F - PLATE_T, PLATE_T)
    plate_r = rrect_y(M2_CX, ZC, PLATE_W, PLATE_H, PLATE_R, Y_LIP_R, PLATE_T)
    # internal parts: the stock 38.6 clearance, inside the cavity outline
    body = rrect_y(M2_CX, ZC, CAV_W - 0.2, 38.6, CAV_R, Y_LIP_F, Y_LIP_R - Y_LIP_F)
    return plate_f.fuse(plate_r).fuse(body)


def build_reference_panel():
    """Full corrected 1U blank.  Reference only, not printable."""
    s = box(0, 0, 0, PANEL_W, PANEL_T, PANEL_H)
    return s.cut(ear_slots(EAR_X).fuse(ear_slots(PANEL_W - EAR_X)))


# ------------------------------------------------------------------- assemble
def main():
    if not os.path.isdir(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    doc = App.newDocument("motu_m2_1u_mount")

    parts = [
        ("PartA_M2_shell", build_part_a()),
        ("PartB_filler", build_part_b()),
        ("TestCoupon_shell", build_coupon()),
        ("REF_M2_spool", build_spool()),
        ("REF_full_panel_1U", build_reference_panel()),
    ]
    objs = {}
    for name, shape in parts:
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        o.Label = name
        objs[name] = o
    doc.recompute()

    report = []
    for name, o in objs.items():
        bb = o.Shape.BoundBox
        report.append("%-20s %7.2f x %7.2f x %7.2f   %8.1f cm3  valid=%s"
                      % (name, bb.XLength, bb.YLength, bb.ZLength,
                         o.Shape.Volume / 1000.0, o.Shape.isValid()))

    doc.saveAs(DOC_PATH)

    for name in ("PartA_M2_shell", "PartB_filler", "TestCoupon_shell"):
        Part.export([objs[name]], os.path.join(EXPORT_DIR, name + ".step"))

    # STL, oriented for printing.  Everything goes face-down: part A and the
    # coupon stand the tube up off the panel (the front rebate's lip is then a
    # 1 mm ledge, nothing to bridge), part B just lies flat.
    def write_stl(shape, name):
        flat = shape.copy()
        flat.rotate(V(0, 0, 0), V(1, 0, 0), 90)      # y -> z: front face on bed
        bb = flat.BoundBox
        flat.translate(V(0, 0, -bb.ZMin))
        m = MeshPart.meshFromShape(Shape=flat, LinearDeflection=0.05,
                                   AngularDeflection=0.30, Relative=False)
        m.write(os.path.join(EXPORT_DIR, name + ".stl"))

    for name in ("PartA_M2_shell", "PartB_filler", "TestCoupon_shell"):
        write_stl(objs[name].Shape, name)

    # ---- sanity checks -----------------------------------------------------
    checks = []

    def line(label, got, want, ok):
        checks.append("%-44s %10.3f  (want %8s)  %s"
                      % (label, got, want, "OK" if ok else "FAIL"))

    def chk(label, got, want, tol):
        line(label, got, "%.3f" % want, abs(got - want) <= tol)

    def atleast(label, got, want):
        line(label, got, ">= %.2f" % want, got >= want - 1e-6)

    chk("panel width", PANEL_W, 482.60, 0.01)
    chk("panel height (1U = 44.45n - 0.79)", PANEL_H, 43.66, 0.10)
    chk("ear horizontal spacing", PANEL_W - 2 * EAR_X, 465.10, 0.01)
    chk("ear vertical spacing", 2 * SLOT_DZ, 31.75, 0.01)
    chk("half-lap total thickness", 2 * LAP_FRONT_T + LAP_GAP, PANEL_T, 0.001)

    atleast("wall above/below the rebates", REB_Z0, 1.50)
    atleast("wall above/below the cavity", CAV_Z0, 2.00)
    atleast("skin beside the rebates", SKIN, 1.50)
    atleast("lip under the plate, sides", (PLATE_W - CAV_W) / 2.0, 0.90)
    atleast("lip under the plate, top/bottom", (PLATE_H - CAV_H) / 2.0, 0.50)
    atleast("cavity height vs measured parts", CAV_H - 38.6, 0.00)
    chk("lip to lip (= PCB length)", Y_LIP_R - Y_LIP_F, SPAN + SPAN_ADJ, 0.001)
    line("front rebate inside the panel", PANEL_T - Y_LIP_F, "> 0", Y_LIP_F < PANEL_T)

    bb = objs["PartA_M2_shell"].Shape.BoundBox
    line("part A inside the 1U envelope (z)", bb.ZMax, "<= %.2f" % PANEL_H,
         bb.ZMin >= -1e-6 and bb.ZMax <= PANEL_H + 1e-6)
    for nm in ("PartA_M2_shell", "PartB_filler"):
        b = objs[nm].Shape.BoundBox
        L = max(b.XLength, b.YLength)
        line(nm + " longest side", L, "< %.0f" % (BED - 2), L < BED - 2)

    line("left web clear of the rack ear", (TUBE_X0 - GUSSET) - (EAR_X + SLOT_TRAVEL / 2 + SLOT_R),
         "> 2", TUBE_X0 - GUSSET > EAR_X + SLOT_TRAVEL / 2 + SLOT_R + 2.0)
    line("right web clear of the half-lap", LAP_X0 - (TUBE_X1 + GUSSET),
         "> 1", TUBE_X1 + GUSSET < LAP_X0 - 1.0)

    # boolean proofs against the M2 stand-in
    a = objs["PartA_M2_shell"].Shape
    spool = objs["REF_M2_spool"].Shape
    line("collision, M2 spool vs part A (mm3)", a.common(spool).Volume, "0", a.common(spool).Volume < 1e-3)
    line("collision, part A vs part B (mm3)", a.common(objs["PartB_filler"].Shape).Volume, "0",
         a.common(objs["PartB_filler"].Shape).Volume < 1e-3)
    # the plates must actually bear on the lips: nudge each plate 0.1 inward
    # and it should hit plastic
    for label, y in (("front", Y_LIP_F - PLATE_T + 0.1), ("rear", Y_LIP_R - 0.1)):
        p = rrect_y(M2_CX, ZC, PLATE_W, PLATE_H, PLATE_R, y, PLATE_T)
        bear = a.common(p).Volume / 0.1
        line("%s plate bearing area on lip (mm2)" % label, bear, "> 300", bear > 300)
    atleast("floor left under the PCB countersinks", CAV_Z0 - M3_CSK_DEPTH, 1.00)
    line("PCB screw pattern inside the cavity floor (x)",
         CAV_W / 2.0 - (PCB_SCREW_DX / 2.0 + PCB_SCREW_TRAVEL / 2.0 + M3_HEAD_R), "> 5",
         CAV_W / 2.0 - (PCB_SCREW_DX / 2.0 + PCB_SCREW_TRAVEL / 2.0 + M3_HEAD_R) > 5.0)
    chk("PCB screw spacing x", PCB_SCREW_X[1] - PCB_SCREW_X[0], PCB_SCREW_DX, 0.001)
    chk("PCB screw spacing y", PCB_SCREW_Y[1] - PCB_SCREW_Y[0], PCB_SCREW_DY, 0.001)
    chk("PCB screws, front row from front face", PCB_SCREW_Y[0], 38.5, 0.5)
    chk("PCB screws, rear row from rear end", Y_END - PCB_SCREW_Y[1], 37.5, 0.5)
    # nothing hangs below the shell, and every screw really pierces the floor
    for x in PCB_SCREW_X:
        for y in PCB_SCREW_Y:
            probe = Part.makeCylinder(0.5, CAV_Z0, V(x, y, 0), V(0, 0, 1))
            line("PCB screw hole open at (%.1f, %.2f)" % (x, y),
                 a.common(probe).Volume, "0", a.common(probe).Volume < 1e-6)
    line("front plate flush with panel face", Y_LIP_F - PLATE_T, "0.000", abs(Y_LIP_F - PLATE_T) < 1e-6)

    with open(os.path.join(EXPORT_DIR, "build-report.txt"), "w") as f:
        f.write("PARTS\n" + "\n".join(report) + "\n\nCHECKS\n" + "\n".join(checks) + "\n")
    print("\n".join(report))
    print()
    print("\n".join(checks))


main()

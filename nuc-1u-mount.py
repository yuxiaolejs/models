#!/usr/bin/env freecad-console
"""
1U rack mount for an Intel NUC 11 slim (117 x 112 x 37 mm).

Forked from rack-panel.FCStd, with the rack geometry corrected to EIA-310:
  - panel width  482.6 mm  (was 482.0)
  - panel height  43.6 mm  (was 44.0; spec is h = 44.45n - 0.79)
  - ear slots 8.75 mm in from each edge -> 465.10 mm centres, and symmetric,
    so a mirrored half no longer lands at 466.0
  - 0.2 mm clearance in the half-lap joint (was an exact 0.0 press fit)

Regenerate with:
  /home/unics/Downloads/FreeCAD_1.1.1-Linux-x86_64-py311.AppImage \
      --console nuc-1u-mount.py < /dev/null

Axes:  X = across the rack, Y = depth (0 = panel front face), Z = up.
"""

import math
import os
import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector as V

OUT_DIR = "/home/unics/Desktop/3dmodels"
DOC_PATH = os.path.join(OUT_DIR, "nuc-1u-mount.FCStd")
EXPORT_DIR = os.path.join(OUT_DIR, "export")

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

# ------------------------------------------------------------------- the NUC
NUC_W = 117.0             # front face width
NUC_D = 112.0
NUC_H = 37.0              # including the rubber feet (~3 mm)
NUC_FIT = 0.60            # clearance per side
NUC_CX = 140.0            # where it sits across the panel (inside part A)

FLOOR_T = 2.80
FLOOR_MARGIN_X = 6.0
FLOOR_TAIL = 5.0          # solid floor left behind the rear countersink; the
                          # tray stops there rather than following the NUC back,
                          # so nothing crowds the rear I/O
NUC_FOOT_H = 3.00         # rubber feet: the chassis body floats this far above
                          # the tray floor, which is what the haunch tucks under

# --- bottom mounting screws ------------------------------------------------
# Two M3 screws in the base of the NUC (the VESA bracket points).  85 mm centre
# distance CONFIRMED on the printed coupon, on a FORE/AFT axis: the pair lies on
# the tray centreline, one ahead of and one behind the floor openings.
M3_SPACING = 85.0
M3_SLOT_TRAVEL = 24.0     # transverse (across-rack) adjustment
M3_OFFSET_Y = 0.0         # shift the pair fore/aft if it isn't centred on the NUC
M3_CLEAR_R = 1.70         # Ø3.4
M3_HEAD_R = 3.00          # Ø6.0 flat head, 90 deg
M3_CSK_DEPTH = 1.30

# ------------------------------------------------------------------- cosmetic
BEZEL_T = 2.00            # front frame standing proud of the panel face
BEZEL_BORDER = 9.00
RAIL_T = 3.00
RAIL_H = 14.00            # continuous side walls -> the tray is a channel section
RAIL_VENT = (12.0, 7.0)   # slot through each rail, so air can still cross

# panel <-> tray reinforcement
FILLET_H = 2.50           # 45 deg haunch, outboard of the NUC where it is free
FILLET_H_NUC = 1.50       # ...and across the pocket, where it tucks under the
                          # chassis in the gap the feet leave (needs < NUC_FOOT_H)
GUSSET_H = 28.00          # corner webs, outboard of the NUC on both sides
NUC_GAP_Y = 0.50          # clearance from the panel back face to the NUC front
VENT_W = 4.00
VENT_PITCH = 9.00

NUC_X0 = NUC_CX - (NUC_W + 2 * NUC_FIT) / 2.0
NUC_X1 = NUC_CX + (NUC_W + 2 * NUC_FIT) / 2.0
# the NUC now sits right up against the panel; the haunch passes underneath it
# rather than in front of it, so the port recess is just the panel + 0.5.
NUC_Y0 = PANEL_T + NUC_GAP_Y
NUC_Y1 = NUC_Y0 + NUC_D
NUC_Z0 = FLOOR_T
NUC_Z1 = NUC_Z0 + NUC_H
NUC_BODY_Z0 = NUC_Z0 + NUC_FOOT_H     # underside of the chassis proper

FLOOR_X0 = NUC_X0 - RAIL_T - FLOOR_MARGIN_X
FLOOR_X1 = NUC_X1 + RAIL_T + FLOOR_MARGIN_X

# mounting slot centres: on the tray centreline, fore and aft
M3_MID_Y = (NUC_Y0 + NUC_Y1) / 2.0 + M3_OFFSET_Y
M3_Y = (M3_MID_Y - M3_SPACING / 2.0, M3_MID_Y + M3_SPACING / 2.0)

# the tray ends just behind the rear screw, not behind the NUC
FLOOR_Y1 = M3_Y[1] + M3_HEAD_R + FLOOR_TAIL

# airflow openings in the tray floor, kept clear of the NUC's rubber feet and
# of the fore/aft mounting slots
VENT_HOLES_X = ((104.0, 136.0), (144.0, 174.0))
VENT_HOLES_Y = tuple((NUC_Y0 + a, NUC_Y0 + b) for a, b in ((22.5, 52.5), (59.5, 89.5)))

WIN_X0 = NUC_X0
WIN_X1 = NUC_X1
WIN_Z0 = NUC_Z0 + FILLET_H_NUC  # window starts above the haunch
WIN_Z1 = NUC_Z1 + 0.2


# --------------------------------------------------------------------- helpers
def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))


def slot_y(xc, zc, r, travel, y0, ylen):
    """Obround in the XZ plane, bored along +Y.  The rack ear slots."""
    a = Part.makeCylinder(r, ylen, V(xc - travel / 2.0, y0, zc), V(0, 1, 0))
    b = Part.makeCylinder(r, ylen, V(xc + travel / 2.0, y0, zc), V(0, 1, 0))
    m = box(xc - travel / 2.0, y0, zc - r, travel, ylen, 2 * r)
    return a.fuse(b).fuse(m)


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
    below the tray floor into the U underneath.
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


def m3_pair(cx, ys, travel):
    """Cutting solids for the two mounting slots, elongated across the rack."""
    out = []
    for y in ys:
        p0, p1 = (cx - travel / 2.0, y), (cx + travel / 2.0, y)
        out.append(slot_z(p0, p1, M3_CLEAR_R, -1.0, FLOOR_T + 2.0))
        out.append(csk_slot_z(p0, p1, M3_HEAD_R, M3_CLEAR_R, M3_CSK_DEPTH, 0.0))
    return out


def web(x, thick, h):
    """45 deg triangular web tying the panel back face to the tray floor.

    Vertical leg against the panel, hypotenuse falling away to the floor, so
    every layer is fully supported by the one below it -- no support material.
    """
    y0, z0 = PANEL_T, FLOOR_T
    pts = [V(x, y0, z0), V(x, y0, z0 + h), V(x, y0 + h, z0)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return f.extrude(V(thick, 0, 0))


def ear_slots(xc):
    """The two rack slots of one ear, as a single cutting solid."""
    lo = slot_y(xc, PANEL_H / 2.0 - SLOT_DZ, SLOT_R, SLOT_TRAVEL, -2.0, PANEL_T + 4.0)
    hi = slot_y(xc, PANEL_H / 2.0 + SLOT_DZ, SLOT_R, SLOT_TRAVEL, -2.0, PANEL_T + 4.0)
    return lo.fuse(hi)


def joint_holes():
    cuts = [Part.makeCylinder(JOINT_HOLE_R, PANEL_T + 4.0, V(SPLIT_C, -2.0, z), V(0, 1, 0))
            for z in JOINT_HOLE_Z]
    return reduce_fuse(cuts)


def reduce_fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out


def vent_field(x0, x1, z0, z1, width=VENT_W, pitch=VENT_PITCH):
    """Vertical slots through the panel, from x0 up to (not past) x1."""
    cuts = []
    x = x0
    while x + width <= x1:
        cuts.append(box(x, -BEZEL_T - 2.0, z0, width, PANEL_T + BEZEL_T + 4.0, z1 - z0))
        x += pitch
    return cuts


# ------------------------------------------------------------------- part A
def build_part_a():
    """Left half: 1U panel + NUC tray."""
    s = box(0, 0, 0, LAP_X1, PANEL_T, PANEL_H)
    # half-lap tongue: keep only the front leaf over the overlap
    s = s.cut(box(LAP_X0, LAP_FRONT_T, -1.0, LAP + 1.0, PANEL_T, PANEL_H + 2.0))

    # front bezel frame around the window
    s = s.fuse(box(WIN_X0 - BEZEL_BORDER, -BEZEL_T, 0,
                   (WIN_X1 - WIN_X0) + 2 * BEZEL_BORDER, BEZEL_T, PANEL_H))

    # tray floor
    s = s.fuse(box(FLOOR_X0, PANEL_T, 0,
                   FLOOR_X1 - FLOOR_X0, FLOOR_Y1 - PANEL_T, FLOOR_T))

    # continuous side walls, running the full depth: these are the tray's
    # edge beams, not just location features
    for xr in (NUC_X0 - RAIL_T, NUC_X1):
        s = s.fuse(box(xr, NUC_Y0, FLOOR_T, RAIL_T, FLOOR_Y1 - NUC_Y0, RAIL_H))

    # haunch along the entire panel/floor junction: full height outboard of the
    # NUC, reduced across the pocket so it slips under the chassis
    s = s.fuse(web(NUC_X0, NUC_X1 - NUC_X0, FILLET_H_NUC))
    # deep corner web outboard of the NUC on each side
    s = s.fuse(web(FLOOR_X0, NUC_X0 - FLOOR_X0, GUSSET_H))
    s = s.fuse(web(NUC_X1, FLOOR_X1 - NUC_X1, GUSSET_H))

    # no rear stops: they fouled the HDMI and DC connectors.  The two screws
    # locate the NUC fore/aft on their own.

    cuts = []

    # window for the NUC front face
    cuts.append(box(WIN_X0, -BEZEL_T - 2.0, WIN_Z0,
                    WIN_X1 - WIN_X0, PANEL_T + BEZEL_T + 4.0, WIN_Z1 - WIN_Z0))

    # rack ear + joint holes
    cuts.append(ear_slots(EAR_X))
    cuts.append(joint_holes())

    # panel vents either side of the bezel
    cuts += vent_field(24.0, WIN_X0 - BEZEL_BORDER - 4.0, 6.0, PANEL_H - 6.0)
    cuts += vent_field(WIN_X1 + BEZEL_BORDER + 4.0, LAP_X0 - 4.0, 6.0, PANEL_H - 6.0)

    # slots through the side walls, clear of the corner webs
    vw, vh = RAIL_VENT
    for xr in (NUC_X0 - RAIL_T, NUC_X1):
        for ys in (NUC_Y0 + 37, NUC_Y0 + 62, NUC_Y0 + 87):
            cuts.append(box(xr - 1.0, ys, FLOOR_T + 4.0, RAIL_T + 2.0, vw, vh))

    # airflow openings in the tray floor (NUC 11 draws in through its base)
    for xa, xb in VENT_HOLES_X:
        for ya, yb in VENT_HOLES_Y:
            cuts.append(box(xa, ya, -1.0, xb - xa, yb - ya, FLOOR_T + 2.0))

    # M3 mounting slots + countersinks, fore and aft on the tray centreline
    cuts += m3_pair(NUC_CX, M3_Y, M3_SLOT_TRAVEL)

    return s.cut(reduce_fuse(cuts))


# ------------------------------------------------------------------- part B
def build_part_b():
    """Right half: plain vented 1U filler."""
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
    """Small plate with just the M3 slot pattern, to check the spacing."""
    w = M3_SLOT_TRAVEL + 34.0
    d = M3_SPACING + 34.0
    s = box(-w / 2.0, 0, 0, w, d, FLOOR_T)
    cy = d / 2.0
    ys = (cy - M3_SPACING / 2.0, cy + M3_SPACING / 2.0)
    cuts = m3_pair(0.0, ys, M3_SLOT_TRAVEL)
    # a stub of the panel so the front datum can be checked too
    s = s.fuse(box(-w / 2.0, 0, 0, w, 2.0, 12.0))
    return s.cut(reduce_fuse(cuts))


# ------------------------------------------------------------- full-panel ref
def build_reference_panel():
    """The original Blank, corrected to EIA-310.  Reference only, not printable."""
    s = box(0, 0, 0, PANEL_W, PANEL_T, PANEL_H)
    return s.cut(ear_slots(EAR_X).fuse(ear_slots(PANEL_W - EAR_X)))


# ------------------------------------------------------------------- assemble
def main():
    if not os.path.isdir(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    doc = App.newDocument("nuc_1u_mount")

    parts = [
        ("PartA_NUC_tray", build_part_a()),
        ("PartB_filler", build_part_b()),
        ("TestCoupon_M3", build_coupon()),
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

    # STEP
    for name in ("PartA_NUC_tray", "PartB_filler", "TestCoupon_M3"):
        Part.export([objs[name]], os.path.join(EXPORT_DIR, name + ".step"))

    # STL, oriented for printing.  Part B is laid flat on its face.
    def write_stl(shape, name):
        m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                   AngularDeflection=0.30, Relative=False)
        m.write(os.path.join(EXPORT_DIR, name + ".stl"))

    write_stl(objs["PartA_NUC_tray"].Shape, "PartA_NUC_tray")
    write_stl(objs["TestCoupon_M3"].Shape, "TestCoupon_M3")
    flat = objs["PartB_filler"].Shape.copy()
    flat.rotate(V(0, 0, 0), V(1, 0, 0), -90)
    write_stl(flat, "PartB_filler")

    # ---- sanity checks -----------------------------------------------------
    checks = []

    def chk(label, got, want, tol):
        ok = abs(got - want) <= tol
        checks.append("%-42s %10.3f  (want %8.3f)  %s"
                      % (label, got, want, "OK" if ok else "FAIL"))
        return ok

    ref = objs["REF_full_panel_1U"].Shape
    chk("panel width", PANEL_W, 482.60, 0.01)
    chk("panel height (1U = 44.45n - 0.79)", PANEL_H, 43.66, 0.10)
    chk("ear horizontal spacing", PANEL_W - 2 * EAR_X, 465.10, 0.01)
    chk("ear vertical spacing", 2 * SLOT_DZ, 31.75, 0.01)
    chk("ear pattern centred on panel", (EAR_X + (PANEL_W - EAR_X)) / 2.0,
        PANEL_W / 2.0, 0.001)
    chk("half-lap total thickness", 2 * LAP_FRONT_T + LAP_GAP, PANEL_T, 0.001)
    chk("NUC top clear of panel top", PANEL_H - NUC_Z1, 3.80, 1.0)
    chk("floor left under countersink", FLOOR_T - M3_CSK_DEPTH, 1.50, 0.5)

    for nm in ("PartA_NUC_tray", "PartB_filler"):
        bb = objs[nm].Shape.BoundBox
        checks.append("%-42s %10.3f  (bed %8.3f)  %s"
                      % (nm + " longest side", max(bb.XLength, bb.YLength), BED,
                         "OK" if max(bb.XLength, bb.YLength) < BED - 2 else "FAIL"))

    # the NUC must actually fit the pocket
    checks.append("%-42s %10.3f  (want %8.3f)  %s"
                  % ("NUC pocket width", NUC_X1 - NUC_X0, NUC_W,
                     "OK" if NUC_X1 - NUC_X0 >= NUC_W else "FAIL"))
    checks.append("%-42s %10.3f  (want %8.3f)  %s"
                  % ("NUC + floor vs panel height", NUC_Z1, PANEL_H,
                     "OK" if NUC_Z1 < PANEL_H else "FAIL"))
    chk("side wall top below NUC top", FLOOR_T + RAIL_H, NUC_Z1 - 20.0, 6.0)
    chk("corner web top below panel top", FLOOR_T + GUSSET_H, PANEL_H - 10.0, 5.0)

    # the haunch now runs under the chassis, so it has to clear the foot gap
    haunch_gap = NUC_BODY_Z0 - (FLOOR_T + FILLET_H_NUC)
    checks.append("%-42s %10.3f  (want %8.3f)  %s"
                  % ("haunch under chassis, clearance", haunch_gap, 0.5,
                     "OK" if haunch_gap >= 0.5 else "FAIL"))
    chk("port recess (panel face to NUC face)", NUC_Y0, PANEL_T + NUC_GAP_Y, 0.001)
    checks.append("%-42s %10.3f  (want %8.3f)  %s"
                  % ("floor tail behind rear countersink",
                     FLOOR_Y1 - (M3_Y[1] + M3_HEAD_R), FLOOR_TAIL,
                     "OK" if FLOOR_Y1 - (M3_Y[1] + M3_HEAD_R) >= FLOOR_TAIL - 1e-6 else "FAIL"))
    checks.append("%-42s %10.3f  (want %8s)  %s"
                  % ("tray stops ahead of NUC rear face", NUC_Y1 - FLOOR_Y1, "> 0",
                     "OK" if FLOOR_Y1 < NUC_Y1 else "FAIL"))

    # M3 countersinks (now fore/aft) must not break into the airflow openings,
    # and must stay on solid floor
    gap = min(VENT_HOLES_Y[0][0] - (M3_Y[0] + M3_HEAD_R),
              (M3_Y[1] - M3_HEAD_R) - VENT_HOLES_Y[-1][1])
    checks.append("%-42s %10.3f  (want %8.3f)  %s"
                  % ("M3 countersink to floor opening", gap, 2.0,
                     "OK" if gap >= 2.0 else "FAIL"))
    chk("M3 pair spacing", M3_Y[1] - M3_Y[0], M3_SPACING, 0.001)
    front_edge = M3_Y[0] - M3_HEAD_R - NUC_Y0
    rear_edge = FLOOR_Y1 - (M3_Y[1] + M3_HEAD_R)
    checks.append("%-42s %10.3f  (want %8.3f)  %s"
                  % ("M3 slots inside the floor (min edge)", min(front_edge, rear_edge),
                     3.0, "OK" if min(front_edge, rear_edge) >= 3.0 else "FAIL"))
    csk_x = M3_SLOT_TRAVEL / 2.0 + M3_HEAD_R
    checks.append("%-42s %10.3f  (want %8.3f)  %s"
                  % ("M3 slot span vs tray width", 2 * csk_x, FLOOR_X1 - FLOOR_X0,
                     "OK" if 2 * csk_x < FLOOR_X1 - FLOOR_X0 else "FAIL"))

    # tray must not reach the joint
    checks.append("%-42s %10.3f  (want %8.3f)  %s"
                  % ("tray clear of half-lap", LAP_X0 - FLOOR_X1, 0.0,
                     "OK" if FLOOR_X1 < LAP_X0 else "FAIL"))

    with open(os.path.join(EXPORT_DIR, "build-report.txt"), "w") as f:
        f.write("PARTS\n" + "\n".join(report) + "\n\nCHECKS\n" + "\n".join(checks) + "\n")
    print("\n".join(report))
    print()
    print("\n".join(checks))


main()

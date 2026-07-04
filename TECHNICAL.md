# The Tetra Factory Death Bug — Technical Breakdown

*Omikron: The Nomad Soul (Quantic Dream, 1999, PC). Research: DesperateOsprey.*

## The symptom

In the Tetra Factory bomb mission, after the pulley crossing over the goo,
players die at full health with no visible cause. The death plays the
réincarnation sequence but consumes no Magic Ring, respawns the player, and
leaves the mission timer running. Surviving the room is timing luck. This has
been reported since at least 2013 on GOG and Steam forums and is documented on
the Omikron fandom wiki as a progression-ending bug.

## The mechanism, end to end

1. Every frame, the engine's mover/displacement handler (`0x4691B0` in
   Runtime.exe, GOG/Steam build, fixed base 0x400000) processes entities that
   move and can carry or push the player.
2. The engine tracks the player's current support/contact entity in a global
   at `0x006A5210` (a handle; handle -> entity record).
3. Each room mesh record carries a dword at record offset +4. On the Tetra
   Factory's train mesh **`TTain04`** this dword is **8** — a lethal-contact
   marker. (The safe floor `TT052` and every other mesh in the room have 0.)
4. When the train's collision sweep captures the player as its
   support/contact — which can happen anywhere along its path during a pass or
   cycle wrap, for roughly half a second — the handler sees:
   *support entity == the processed entity AND its lethal dword has bit 8*
   (check at `0x469302`), and calls `PersoGoToMove(player, -1)` (`0x469310`).
5. Move `-1` is the death/réincarnation path: `0x423FC0` starts the
   réincarnation (move bank 0xC9), a 60-tick timer at `0x4E975C` runs, and
   completion (`0x427AC0`, state `[perso+0x194]` 0xF -> 3) plays the recovery
   bank 0xC8. **No ring is consumed because this scripted-death path bypasses
   the normal kill accounting entirely** — which is also why the réincarnation
   display shows a ring being "used" without the counter decrementing (the
   long-standing community observation).

So the machinery works exactly as designed; the defect is one data value:
the train mesh is flagged lethal, in a room whose mandatory route overlaps the
train's collision sweep.

## The fix

`MESHES\DECORS\STtra03.3DO`, offset `0x7C478`: `08 -> 00`.

The record on disk is byte-identical to the in-memory record that was
live-verified (zeroing the field in memory made the death unreproducible over
multiple train cycles, while acid deaths continued to work and decrement
rings). The on-disk patch was then verified end-to-end from a clean game
start: full crossing, multiple train cycles, bomb placement, and a control
acid death, all behaving correctly.

## Why this was hard to find

- Nothing ever *writes* the kill flag during the bug — it's a static property
  of the train mesh, so every "find what writes" watch in every session came
  back empty by design.
- The kill call chain only exists for ~0.5 s per event, and the deep stack
  frames contain stale return addresses that pointed investigations at the
  animation system.
- The réincarnation that follows is a *designed* mechanic (a ring-free
  scripted death used elsewhere in the game), so the death sequence itself
  always looked "intentional" under instrumentation.
- The support-entity flip that actually gates the kill was captured by a
  memory poller twice before its meaning was understood.

## Tooling

- Cheat Engine (VEH debugger) for live breakpoints and stack captures.
- pymem pollers for high-rate transition logging of the kill flag, the
  réincarnation state machine, and the support-entity global.
- Offline: objdump disassembly of Runtime.exe, custom parsers for the IAM
  AREA/SCENE containers and the zone-action script VM (opcode table at
  0x4C0140), and struct dumps that surfaced the mesh names.
- Community groundwork: stu_pidd_cow's 3DO format documentation (mesh records
  with name, bounding sphere/box, flags — including 0x800000 Collision-Only)
  and Chevluh's Blender importer.

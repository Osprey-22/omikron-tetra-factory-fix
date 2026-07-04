# Omikron: The Nomad Soul — Tetra Factory Death Fix

**Fixes the infamous game-breaking bug in the Tetra Factory bomb mission** where
your character randomly dies after the pulley/hook crossing — the "mysterious
death at full health" documented in Steam and GOG forums since at least 2013.

## What the bug is

During the timed bomb mission in the Tetra Factory (Jaunpur), the area after
you cross the green goo on the factory pulley kills players seemingly at
random. You die at full health, a forced "réincarnation" plays (no Magic Ring
is consumed), you're placed back, and the mission timer keeps running. Whether
you survive the room is effectively luck; many players could never finish the
mission and abandoned the game here.

## What actually causes it

The moving train in that room (mesh `TTain04` in the room file `STtra03.3DO`)
is flagged **lethal on contact** in the game data. The train's collision sweep
periodically "captures" the player as standing on it — including at moments
when the train isn't visibly near you — and one frame of contact with a
lethal-flagged mesh triggers the forced death. The old community folklore
("the train's hitbox is stupidly off") was pointing at the right object.

## What the patch does

Changes **one byte** in one file:

```
File:   MESHES\DECORS\STtra03.3DO
Offset: 0x7C478
Change: 08 -> 00
```

This clears the lethal-contact flag on the train mesh. The train still moves,
animates, and behaves normally — it just can't instantly kill you anymore.
Nothing else is touched: acid deaths, enemies, mission scripting, and Magic
Ring accounting all work exactly as before. Verified on the Steam release;
the same file ships with the GOG release.

## How to apply

**Option A — patcher script (recommended):**
1. Install Python 3 if you don't have it.
2. Close the game.
3. Run: `python patch_train.py "<path to your Omikron folder>"`
   e.g. `python patch_train.py "C:\Program Files (x86)\Steam\steamapps\common\Omikron"`
4. The script verifies the file before writing, creates a backup
   (`STtra03.3DO.orig`), and changes the single byte.

To undo: `python patch_train.py "<path>" --revert`

**Option B — manual (any hex editor):**
1. Back up `MESHES\DECORS\STtra03.3DO`.
2. Open it in a hex editor, go to offset `0x7C478`.
3. Confirm the byte there is `08` and that offset `0x7C484` reads `TTain04`.
4. Change `08` to `00`, save.

## Verification

Original file (unpatched):
- Size:  <SIZE> bytes
- MD5:   <MD5>
- SHA-1: <SHA1>

The patcher refuses to write if the file doesn't match the expected layout, so
it cannot damage a file from a different version.

## Credits

Research, live debugging, and testing: **DesperateOsprey**
Built on community groundwork: stu_pidd_cow's Omikron format documentation and
Chevluh's Blender importer.

If this patch saved your playthrough, you can support the work here:
<[BUYMEACOFFEE LINK](https://buymeacoffee.com/desperateosprey)>

This patch distributes no copyrighted game data — it is a description of a
one-byte change plus a script that applies it to files you already own.

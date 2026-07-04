#!/usr/bin/env python3
"""patch_train.py — Omikron: The Nomad Soul, Tetra Factory train-death fix.

Clears the lethal-contact flag on the train mesh "TTain04" in the Tetra
Factory room (STtra03.3DO), which causes the well-known false death /
ring-free forced réincarnation after the pulley crossing during the bomb
mission. The train still moves, animates, and collides normally; genuine
hazards (acid, enemies) are unaffected.

Patch: MESHES\\DECORS\\STtra03.3DO, offset 0x7C478: 08 -> 00 (one byte).

Usage:
  python patch_train.py "C:\\SteamLibrary\\steamapps\\common\\Omikron"
  python patch_train.py "C:\\SteamLibrary\\steamapps\\common\\Omikron" --revert

Creates STtra03.3DO.orig on first run. --revert restores it.
"""
import os, sys, shutil

REL = os.path.join("MESHES", "DECORS", "STtra03.3DO")
OFFSET = 0x7C478
NAME_OFF = 0x7C484
EXPECT_NAME = b"TTain04\x00"
EXPECT_BEFORE = bytes.fromhex("04 00 00 00 08 00 00 00".replace(" ", ""))  # at 0x7C474
PATCHED_AT4 = 0x00

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    revert = "--revert" in sys.argv
    path = os.path.join(root, REL)
    orig = path + ".orig"
    if not os.path.isfile(path):
        sys.exit(f"not found: {path}")

    if revert:
        if not os.path.isfile(orig):
            sys.exit("no .orig backup found; nothing to revert.")
        shutil.copy2(orig, path)
        print("reverted from backup.")
        return

    data = bytearray(open(path, "rb").read())
    if data[NAME_OFF:NAME_OFF + len(EXPECT_NAME)] != EXPECT_NAME:
        sys.exit("verification failed: 'TTain04' not at expected offset — wrong file/version. Nothing changed.")
    block = bytes(data[0x7C474:0x7C47C])
    if block == EXPECT_BEFORE:
        pass  # unpatched, proceed
    elif data[OFFSET] == PATCHED_AT4 and block[:4] == EXPECT_BEFORE[:4]:
        print("already patched. nothing to do.")
        return
    else:
        sys.exit(f"verification failed: bytes at 0x7C474 are {block.hex(' ')} — unexpected. Nothing changed.")

    if not os.path.isfile(orig):
        shutil.copy2(path, orig)
        print(f"backup written: {orig}")
    data[OFFSET] = PATCHED_AT4
    open(path, "wb").write(data)
    print(f"patched: {REL} @ {OFFSET:#x}: 08 -> 00")
    print("train contact death removed. restart the game before testing.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import sys
import re
from pathlib import Path

from pymatgen.core import Lattice, Structure

RY_TO_EV = 13.605693009


def parse_total_energy(text: str):
    """最後の '!    total energy' を拾う"""
    m = re.findall(r"!\s*total energy\s*=\s*([-\d\.]+)\s*Ry", text)
    if not m:
        return None
    e_ry = float(m[-1])
    return e_ry, e_ry * RY_TO_EV


def parse_cell_parameters(lines):
    """最後の CELL_PARAMETERS ブロック (3 行) を読む"""
    idxs = [
        i for i, l in enumerate(lines)
        if l.strip().startswith("CELL_PARAMETERS")
    ]
    if not idxs:
        return None
    i = idxs[-1]
    try:
        v1 = [float(x) for x in lines[i + 1].split()]
        v2 = [float(x) for x in lines[i + 2].split()]
        v3 = [float(x) for x in lines[i + 3].split()]
    except Exception as e:
        raise RuntimeError(f"Failed to parse CELL_PARAMETERS block at line {i+1}") from e
    return [v1, v2, v3]


def parse_atomic_positions(lines):
    """最後の ATOMIC_POSITIONS (crystal) ブロックを読む"""
    idxs = [
        i for i, l in enumerate(lines)
        if l.strip().startswith("ATOMIC_POSITIONS") and "crystal" in l
    ]
    if not idxs:
        return None, None
    i = idxs[-1]

    species = []
    coords = []

    for line in lines[i + 1 :]:
        if not line.strip():
            break
        parts = line.split()
        if len(parts) < 4:
            break
        sp = parts[0]
        try:
            x, y, z = map(float, parts[1:4])
        except ValueError:
            break
        species.append(sp)
        coords.append([x, y, z])

    return species, coords


def main():
    if len(sys.argv) < 2:
        print("使い方: qe_extract_final_cif.py QE_OUTPUT [OUT.cif]")
        sys.exit(1)

    out_file = Path(sys.argv[1])
    cif_file = (
        Path(sys.argv[2])
        if len(sys.argv) >= 3
        else out_file.with_suffix("").with_suffix("").with_name("llzo_relaxed.cif")
    )

    text = out_file.read_text()
    lines = text.splitlines()

    # エネルギー
    e = parse_total_energy(text)
    if e is None:
        print("ERROR: '!    total energy' が見つかりませんでした", file=sys.stderr)
        sys.exit(1)
    e_ry, e_ev = e

    # セル
    cell = parse_cell_parameters(lines)
    if cell is None:
        print("ERROR: CELL_PARAMETERS ブロックが見つかりませんでした", file=sys.stderr)
        sys.exit(1)
    lattice = Lattice(cell)

    # 原子位置
    species, coords = parse_atomic_positions(lines)
    if species is None:
        print("ERROR: ATOMIC_POSITIONS (crystal) ブロックが見つかりませんでした", file=sys.stderr)
        sys.exit(1)

    struct = Structure(lattice, species, coords)

    # 出力
    print(f"=== {out_file.name} ===")
    print(f"Total energy: {e_ry:.11f} Ry  ({e_ev:.8f} eV)")
    a, b, c = lattice.lengths
    alpha, beta, gamma = lattice.angles
    print("Cell parameters (Angstrom, degrees):")
    print(f"  a = {a:.6f}, b = {b:.6f}, c = {c:.6f}")
    print(f"  α = {alpha:.4f}, β = {beta:.4f}, γ = {gamma:.4f}")
    print()
    print("Number of atoms:", len(struct))

    struct.to(filename=str(cif_file), fmt="cif")
    print(f"\nCIF を出力しました: {cif_file}")


if __name__ == "__main__":
    main()

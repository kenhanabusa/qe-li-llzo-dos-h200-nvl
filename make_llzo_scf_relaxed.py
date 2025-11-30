#!/usr/bin/env python3
from pymatgen.core import Structure
from pymatgen.io.pwscf import PWInput

# 1. 緩和済み構造の読み込み
struct = Structure.from_file("llzo_relaxed.cif")

# 2. 擬ポテンシャルの対応
pseudo = {
    "La": "La.pbe-spfn-rrkjus_psl.1.0.0.UPF",
    "Li": "Li.pbe-s-van_ak.UPF",
    "O":  "O.pbe-rrkjus.UPF",
    "Zr": "Zr.pbe-spn-rrkjus_psl.1.0.0.UPF",
}

# 3. &CONTROL
control = {
    "calculation": "scf",
    "prefix": "llzo_relaxed",
    "outdir": "./tmp/llzo_relaxed",
    "pseudo_dir": "./pseudo",
    "verbosity": "high",
}

# 4. &SYSTEM
system = {
    "ibrav": 0,                # CIF から直接セルを渡すので ibrav=0
    "nat": len(struct),
    "ntyp": len(set(site.species_string for site in struct)),
    "ecutwfc": 50.0,
    "ecutrho": 400.0,
    "occupations": "smearing",
    "smearing": "mp",
    "degauss": 0.02,
}

# 5. &ELECTRONS
electrons = {
    "conv_thr": 1.0e-8,
    "mixing_beta": 0.7,
}

# 6. k 点 (今までと同じ 2x2x2 程度)
kpoints_grid = (2, 2, 2)
kpoints_shift = (0, 0, 0)

pw = PWInput(
    struct,
    pseudo=pseudo,
    control=control,
    system=system,
    electrons=electrons,
    kpoints_grid=kpoints_grid,
    kpoints_shift=kpoints_shift,
)

with open("llzo_scf_relaxed.in", "w") as f:
    f.write(str(pw))

print("SCF 入力を書き出しました: llzo_scf_relaxed.in")

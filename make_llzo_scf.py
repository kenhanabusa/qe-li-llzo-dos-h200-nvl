#!/usr/bin/env python

from pymatgen.io.cif import CifParser
from pymatgen.io.pwscf import PWInput  # ★ ここがポイント

# ==== 1. CIF から構造を読む ====

cif_file = "llzo_bulk.cif"
parser = CifParser(cif_file)

# get_structures() は非推奨なので parse_structures を使用
structures = parser.parse_structures(primitive=False)
struct = structures[0]

print("構造を読み込みました:")
print(struct)
print(f"サイト数 = {len(struct.sites)}")

# ==== 2. 擬ポテンシャル対応 ====
#   qe_gpu_test/pseudo/ にあるファイル名と対応させる

pseudo = {
    "Li": "Li.pbe-s-van_ak.UPF",
    "La": "La.pbe-spfn-rrkjus_psl.1.0.0.UPF",
    "Zr": "Zr.pbe-spn-rrkjus_psl.1.0.0.UPF",
    "O":  "O.pbe-rrkjus.UPF",
}

# ==== 3. &CONTROL / &SYSTEM / &ELECTRONS の設定 ====

control = {
    "calculation": "scf",
    "prefix": "llzo_bulk",
    "pseudo_dir": "./pseudo",
    "outdir": "./tmp/llzo_bulk",
}

system = {
    "ecutwfc": 50.0,   # 後で必要に応じて上げても良い
    "ecutrho": 400.0,
    "occupations": "smearing",
    "smearing": "mp",
    "degauss": 0.02,
}

electrons = {
    "conv_thr": 1.0e-8,
    "mixing_beta": 0.7,
}

# ==== 4. k 点メッシュ ====
kgrid = (2, 2, 2)
kshift = (0, 0, 0)

pwinput = PWInput(
    struct,
    pseudo=pseudo,
    control=control,
    system=system,
    electrons=electrons,
    kpoints_mode="automatic",
    kpoints_grid=kgrid,
    kpoints_shift=kshift,
)

output_in = "llzo_scf.in"
pwinput.write_file(output_in)

print(f"\nQuantum ESPRESSO 用入力ファイルを書き出しました: {output_in}")
print("このファイルを例えば次のように実行できます:")
print("  mpirun -np 4 pw.x -inp llzo_scf.in")

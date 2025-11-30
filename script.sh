cat > make_llzo_scf.py << 'EOF'
from pymatgen.io.cif import CifParser
from pymatgen.io.qe import PWInput

# === 1. CIF を読む ===
parser = CifParser("llzo_bulk.cif")
# 将来のために parse_structures を使う書き方
structure = parser.parse_structures(primitive=False)[0]

print("構造情報:")
print("  組成:", structure.composition)
print("  原子数 nat   :", len(structure))
print("  元素数 ntyp  :", len(structure.composition.elements))
print("  格子定数 (Å):", structure.lattice.abc)
print("  角度 (deg)  :", structure.lattice.angles)

# === 2. 擬ポテンシャルの対応 ===
pseudo = {
    "Li": "Li.pbe-s-van_ak.UPF",
    "La": "La.pbe-spfn-rrkjus_psl.1.0.0.UPF",
    "Zr": "Zr.pbe-spn-rrkjus_psl.1.0.0.UPF",
    "O" : "O.pbe-rrkjus.UPF",
}

# === 3. QE の入力パラメータ ===
control = {
    "calculation": "scf",
    "prefix": "llzo",
    "outdir": "./tmp",
    "pseudo_dir": "./pseudo",
    "tprnfor": True,
    "tstress": True,
    "verbosity": "high",
}

system = {
    "ibrav": 0,  # CIF からの一般格子 → ibrav=0 + CELL_PARAMETERS
    "nat": len(structure),
    "ntyp": len(structure.composition.elements),
    "ecutwfc": 80.0,   # とりあえず少し高めに
    "ecutrho": 640.0,  # 通常 8〜12×ecutwfc
    "occupations": "smearing",
    "degauss": 0.02,
}

electrons = {
    "conv_thr": 1.0e-8,
    "mixing_beta": 0.3,
    "electron_maxstep": 100,
}

# 体積 ~1100 Å^3 程度なので、とりあえず 2x2x2 メッシュから
kpoints_grid = (2, 2, 2)

# === 4. PWInput を生成 ===
pwinput = PWInput(
    structure=structure,
    pseudo=pseudo,
    control=control,
    system=system,
    electrons=electrons,
    kpoints_grid=kpoints_grid,
)

# === 5. ファイルに書き出し ===
outname = "llzo_scf.in"
pwinput.write_file(outname)
print(f"\nQE 入力ファイルを書き出しました: {outname}")
EOF
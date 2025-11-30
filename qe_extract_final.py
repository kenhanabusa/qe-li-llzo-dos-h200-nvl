#!/usr/bin/env python3
import sys
import math
import re
from pathlib import Path


BOHR_TO_ANG = 0.529177210903
RY_TO_EV = 13.605693009


def parse_qe_output(path: Path):
    text = path.read_text(errors="ignore")
    lines = text.splitlines()

    # ==== 1) 最終の total energy (Ry, eV) を取得 ====
    energy_ry = None
    energy_line = None
    for line in lines:
        if "!    total energy" in line:
            energy_line = line
    if energy_line:
        m = re.search(r"=\s*([-\d\.Ee+]+)\s*Ry", energy_line)
        if m:
            try:
                energy_ry = float(m.group(1))
            except ValueError:
                pass

    # ==== 2) 最後の "Begin final coordinates" 以降を基準位置に ====
    search_start = 0
    for i, line in enumerate(lines):
        if "Begin final coordinates" in line:
            search_start = i

    # ==== 3) 最後の CELL_PARAMETERS ブロック ====
    cell_idx = None
    for i in range(search_start, len(lines)):
        if lines[i].strip().startswith("CELL_PARAMETERS"):
            cell_idx = i

    cell_vectors = None
    cell_unit = None
    alat_bohr = None

    if cell_idx is not None and cell_idx + 3 < len(lines):
        header = lines[cell_idx].strip()
        # 単位判定
        if "angstrom" in header.lower():
            cell_unit = "angstrom"
        elif "bohr" in header.lower():
            cell_unit = "bohr"
        else:
            m = re.search(r"alat\s*=\s*([-\d\.Ee+]+)", header)
            if m:
                try:
                    alat_bohr = float(m.group(1))
                    cell_unit = "alat"
                except ValueError:
                    pass

        vecs = []
        for j in range(cell_idx + 1, cell_idx + 4):
            parts = lines[j].split()
            if len(parts) >= 3:
                try:
                    vecs.append([float(parts[0]), float(parts[1]), float(parts[2])])
                except ValueError:
                    break
        if len(vecs) == 3:
            cell_vectors = vecs

    # ==== 4) セル長さ a,b,c と角度 α,β,γ を計算 ====
    cell_params = None
    if cell_vectors is not None:
        a_vec, b_vec, c_vec = cell_vectors

        def norm(v):
            return math.sqrt(sum(x * x for x in v))

        def angle(u, v):
            dot = sum(ui * vi for ui, vi in zip(u, v))
            nu, nv = norm(u), norm(v)
            if nu == 0 or nv == 0:
                return None
            cosang = max(-1.0, min(1.0, dot / (nu * nv)))
            return math.degrees(math.acos(cosang))

        # ベクトルが今何の単位か判定
        if cell_unit == "angstrom":
            scale = 1.0
        elif cell_unit == "bohr":
            scale = BOHR_TO_ANG
        elif cell_unit == "alat" and alat_bohr is not None:
            scale = alat_bohr * BOHR_TO_ANG
        else:
            scale = 1.0  # わからない場合はそのまま

        a_len = norm([x * scale for x in a_vec])
        b_len = norm([x * scale for x in b_vec])
        c_len = norm([x * scale for x in c_vec])
        alpha = angle(b_vec, c_vec)
        beta = angle(a_vec, c_vec)
        gamma = angle(a_vec, b_vec)
        cell_params = (a_len, b_len, c_len, alpha, beta, gamma)

    # ==== 5) 最終 ATOMIC_POSITIONS ブロック ====
    apos_idx = None
    for i in range(search_start, len(lines)):
        if lines[i].strip().startswith("ATOMIC_POSITIONS"):
            apos_idx = i

    coord_header = None
    atomic_positions = []
    if apos_idx is not None:
        coord_header = lines[apos_idx].strip()
        for j in range(apos_idx + 1, len(lines)):
            line = lines[j]
            s = line.strip()
            if not s:
                break
            if s.startswith("CELL_PARAMETERS") or s.startswith("End final") \
               or s.startswith("ATOMIC_SPECIES") or s.startswith("K_POINTS") \
               or s.startswith("Sym. Ops"):
                break
            atomic_positions.append(line.rstrip("\n"))

    # ==== 6) まとめて表示 ====
    print(f"=== {path} ===")

    if energy_ry is not None:
        print(f"Total energy: {energy_ry:.8f} Ry  ({energy_ry * RY_TO_EV:.8f} eV)")
    else:
        print("Total energy: (見つかりませんでした)")

    if cell_params is not None:
        a_len, b_len, c_len, alpha, beta, gamma = cell_params
        print("Cell parameters (Angstrom, degrees):")
        print(f"  a = {a_len:.6f}, b = {b_len:.6f}, c = {c_len:.6f}")
        print(f"  α = {alpha:.4f}, β = {beta:.4f}, γ = {gamma:.4f}")
    else:
        print("CELL_PARAMETERS ブロックが見つからなかったか、解析できませんでした。")

    if coord_header:
        print()
        print(coord_header)
        for line in atomic_positions:
            print(line)
    else:
        print()
        print("最終 ATOMIC_POSITIONS ブロックが見つかりませんでした。")

    print()  # 区切り


def main():
    if len(sys.argv) < 2:
        print("使い方: qe_extract_final.py OUTFILE1 [OUTFILE2 ...]")
        sys.exit(1)

    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.is_file():
            print(f"{path}: ファイルが見つかりません。")
            continue
        parse_qe_output(path)


if __name__ == "__main__":
    main()

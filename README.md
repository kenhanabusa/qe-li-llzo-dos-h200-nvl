# Li bcc and LLZO DOS example

This directory contains the input files and scripts used to compute and
plot the density of states (DOS) of metallic Li (bcc) and LLZO using
Quantum ESPRESSO 7.4.1 on an H200 NVL GPU server.

## Requirements

- Quantum ESPRESSO (pw.x, dos.x) with GPU support
- MPI environment
- gnuplot

## How to run (outline)

1. Download the required pseudopotentials and put them into `pseudo/`.
2. Run the Li SCF and DOS:
   - `mpirun -np 4 pw.x -in li_bcc_scf.in`
   - `mpirun -np 1 dos.x -in li_bcc_dos.in`
3. Relax LLZO and run SCF / DOS using the provided `llzo_*.in` files.
4. Convert DOS to energy relative to E_F and plot:
   - `gnuplot plot_li_llzo_dos.gp`

See the blog post on server-gear.com for more detailed explanation.

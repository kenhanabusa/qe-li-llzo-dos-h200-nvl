set terminal pngcairo size 1400,800
set output 'dos_li_vs_llzo_EminusEF.png'
set xlabel 'Energy relative to E_F (eV)'
set ylabel 'DOS (states/eV)'
set grid ytics
set key outside top right
set border lw 1.2
set tics nomirror
set format y '%.2f'
set yrange [0:*]
set xrange [-8:8]
set arrow 1 from 0,graph 0 to 0,graph 1 nohead lw 1 dt 3  # E=0 のガイド線
# 負の微小値（数値誤差）は 0 にクリップ
plot \
  'li_bcc.dos.rel' using 1:( $2>0 ? $2 : 0 ) with lines lw 2 title 'Li bcc (metal)', \
  'llzo.dos.rel'   using 1:( $2>0 ? $2 : 0 ) with lines lw 2 title 'LLZO (insulator)'

#!/bin/bash
# stills.sh COMP t1 t2 ... → ../st_COMP_t.png (seconds)
cd "$(dirname "$0")/.."
BR=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
c=$1; shift
for t in "$@"; do f=$(python3 -c "print(round($t*24))"); npx remotion still src2/indexdev.jsx $c ../st_${c}_$t.png --frame=$f --gl=swiftshader --browser-executable=$BR --log=error < /dev/null 2>&1 | grep -v "^$" | head -5; done

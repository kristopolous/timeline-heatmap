#!/usr/bin/zsh

blank_webp=8fcece1f2f1d2a73e919df74e4d9cabe
blank_png=9f016400e0ff27503782a692c875e8ce
blank=$blank_png

opts=(-contrast-stretch 0 -define webp:sns-strength=25 -define webp:filter-sharpness=6 -define webp:filter-strength=10)
clear() {
  echo "removing tiles ..."
  rm -r tiles
}

create() {
  echo "creating new ones ..."
  vips dzsave heatmap.png tiles --tile-size 256 --overlap 0 --layout google --suffix ".png"
  convert tiles/blank.png -negate tiles/blank.png
}

blur() {
  for z in {0..5}; do
    radius=$(( (6.0 - z)))  # z=0 gets radius 5, z=4 gets radius 1
    echo $z - $radius
    for file in tiles/$z/*/*.png; do
      [[ $(md5sum $file | cut -d ' ' -f 1) == $blank ]] || convert "$file" -morphology Dilate Disk:$radius ${opts[@]} "${file/png/webp}"
    done
  done
}

final() {
  for z in {6..11}; do
    echo $z
    n=0
    for file in tiles/$z/*/*.png; do
      [[ $(md5sum $file | cut -d ' ' -f 1) == $blank ]] || convert "$file" ${opts[@]} "${file/png/webp}"
      (( n++ ))
      if [[ $n == 100 ]]; then 
        echo -n "."
        n=0
      fi
    done
    echo
  done
}

clear
create
blur
final

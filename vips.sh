#!/usr/bin/zsh

create() {
  vips dzsave heatmap.png tiles --tile-size 256 --overlap 0 --layout google --suffix ".webp[Q=90]"
  convert tiles/blank.png -negate tiles/blank.png
}

blur() {
  for z in {0..5}; do
    echo $z
    radius=$(( (6.0 - z) / 4))  # z=0 gets radius 5, z=4 gets radius 1
    for file in tiles/$z/*/*.webp; do
      convert "$file" -morphology Dilate Disk:$radius -contrast-stretch 0 "$file"
    done
  done
}

final() {
  for z in {6..11}; do
    echo $z
    for file in tiles/$z/*/*.webp; do
      convert "$file" -contrast-stretch 0 "$file"
    done
  done
}

echo "removing tiles ..."
rm -r tiles
echo "creating new ones ..."

create
blur
final

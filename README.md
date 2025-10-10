<img width="2635" height="1139" alt="heatmap" src="https://github.com/user-attachments/assets/334fa540-fd23-4243-8fe2-7f379b284f6d" />
# Make a zoommable pannable heatmap of your location history

## Step 1: Get your data
https://github.com/user-attachments/assets/35fe220b-381b-4499-b7d9-01699557749b

## Step 2: Get it over to a computer
Email it, adb, bluetooth, there's plenty of ways.

## Step 3: Tweak the heatmap_generator.py to your likings
- The distance is in lat/lng from the initial location
- The size is in pixels, it will generate a square image.

## Step 4: Run the script with your Timeline.json there
This will take a while and you might need a lot of memory.
When you are done you should have a `heatmap.png`

## Step 5: Install vips, imagemagick && run the tile maker
This is what will break things up into tiles

```shell
$ sudo apt install libvips-tools imagemagick
```

Then try
```shell
$ ./vips.sh
```

You may have to tweak it depending on how many zoom-levels you generate

## Step 6: You're actually done
Open up `index.html` and you'll get something like mine [over here](https://9ol.es/map)

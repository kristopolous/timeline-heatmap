<img width="2635" height="1139" alt="heatmap" src="https://github.com/user-attachments/assets/334fa540-fd23-4243-8fe2-7f379b284f6d" />

# Make a zoommable pannable heatmap of your location history

## Step 1: Get your data
On an Android phone go to settings and you're going to be downloading your location history locally, on to your phone as "Timeline.json"

Then you will transfer it to your computer. Here's a video

https://github.com/user-attachments/assets/35fe220b-381b-4499-b7d9-01699557749b

## Step 2: Get it over to a computer
Email it, adb, bluetooth, there's plenty of ways. Mine is about 10MB/year.

## Step 3: Tweak the heatmap_generator.py to your likings
There's 2 constants at the top of the file

```python
SIZE = 50000
DISTANCE = 15 
```
- The size is in pixels, it will generate a square image, so in this instance 50,000x50,000
- The distance is in lat/lng from the initial location

## Step 4: Run the script with your Timeline.json there
This will take a while and you might need a lot of memory (tens of GB depending on the size)
When you are done you should have a `heatmap.png`.

## Step 5: Install vips, imagemagick && run the tile maker
This is what will break things up into tiles

```shell
$ sudo apt install libvips-tools imagemagick
```

Then try
```shell
$ ./vips.sh
```

You may have to tweak it depending on how many zoom-levels you generate.

## Step 6: You're actually done
Open up `index.html` and you'll get something like mine [over here](https://9ol.es/map). This serves completely statically, so you can just do something like

```shell
$ rsync -azv index.html tiles your-webserver:some-path/
```

And you should be ready to go without any additional futzing around.

## Notes

 - The code is intentionally simple. If something doesn't work, don't be afraid to crack it open and modify it. It's 200 lines, total.
 - The heatmap_generator has a lot to be desired - it could be optimized, parallelized, yeah sure - I'll take PRs.
 - The lower zooms are intentionally dilated so that regions are easy to find.
 - Yes things *do* look stretched mostly because our maps are stretched. This can certainly look "more normal" by squishing it ... go ahead and send me a PR if you want to do the work.

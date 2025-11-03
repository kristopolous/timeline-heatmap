#!/usr/bin/env python3
SIZE = 100000
DISTANCE = 9

import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import logging
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
import math
import colorsys
import png
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def load_locations(file_path, max_degree_delta=DISTANCE):
    """Load locations from JSON file and filter based on proximity to the first location."""
    logging.info("Loading and filtering locations...")
    locations = []
    first_location = None
    total_locations = 0  # Counter for total locations loaded
    unhandled_location_types = set()  # Track unhandled location types
    with open(file_path, 'r') as f:
        data = json.load(f)
        segments = data['semanticSegments']
        for segment in segments:
            if 'timelinePath' in segment:
                for point in segment['timelinePath']:
                    total_locations += 1
                    try:
                        lat, lng = map(float, point['point'].replace('°', '').split(', '))
                        if first_location is None:
                            first_location = (lat, lng)
                        if first_location is not None and abs(lat - first_location[0]) <= max_degree_delta and abs(lng - first_location[1]) <= max_degree_delta:
                            locations.append((lat, lng))
                    except ValueError:
                        print(f"Skipping invalid point: {point['point']}")
            elif 'visit' in segment and 'placeLocation' in segment['visit']['topCandidate']:
                total_locations += 1
                try:
                    lat, lng = map(float, segment['visit']['topCandidate']['placeLocation']['latLng'].replace('°', '').split(', '))
                    if first_location is None:
                        first_location = (lat, lng)
                    if first_location is not None and abs(lat - first_location[0]) <= max_degree_delta and abs(lng - first_location[1]) <= max_degree_delta:
                        locations.append((lat, lng))
                except ValueError:
                    print(f"Skipping invalid visit: {segment['visit']['topCandidate']['placeLocation']['latLng']}")
            elif 'activity' in segment:
                try:
                    lat_start, lng_start = map(float, segment['activity']['start']['latLng'].replace('°', '').split(', '))
                    lat_end, lng_end = map(float, segment['activity']['end']['latLng'].replace('°', '').split(', '))

                    if first_location is None:
                        first_location = (lat_start, lng_start)

                    if first_location is not None and abs(lat_start - first_location[0]) <= max_degree_delta and abs(lng_start - first_location[1]) <= max_degree_delta:
                        locations.append((lat_start, lng_start))
                    if first_location is not None and abs(lat_end - first_location[0]) <= max_degree_delta and abs(lng_end - first_location[1]) <= max_degree_delta:
                        locations.append((lat_end, lng_end))
                    total_locations += 2  # Count both start and end locations
                except (ValueError, KeyError, TypeError) as e:
                    print(f"Skipping invalid activity: {segment['activity']}")
            else:
                # Log unhandled segment types
                segment_type = segment.keys()
                unhandled_location_types.add(str(segment_type))

    logging.info(f"Total locations loaded from file: {total_locations}")  # Log total locations
    logging.info(f"Loaded {len(locations)} locations within {max_degree_delta} degrees of the first location.")
    if unhandled_location_types:
        logging.warning(f"Unhandled location types: {unhandled_location_types}")
    return locations, first_location

# 1. Create the rainbow palette
palette_size = 255
palette = [(0,0,0)]
for i in range(palette_size):
    hue = float(i) / palette_size  # Hue varies from 0 to 1
    r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 0.9)  # S=0.5, V=0.5
    palette.append((int(r * 255), int(g * 255), int(b * 255)))

def mercator_projection(lat, lon):
    """Converts lat/lon to Mercator projection coordinates."""
    r_major = 6378137.0
    x = r_major * math.radians(lon)
    scale = x / lon
    y = r_major * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y

def create_heatmap(locations, width=SIZE, height=SIZE, output_path="heatmap.png"):
    """Create a geographically-constrained heatmap with Mercator projection and normalization in HSV space."""
    logging.info("Creating heatmap...")

    if not locations:
        print("No locations to plot.")
        return

    # Project locations to Mercator coordinates
    logging.info("Projecting points...")
    projected_locations = [mercator_projection(lat, lng) for lat, lng in locations]

    logging.info("Making array...")
    # Get x and y values
    x_vals, y_vals = zip(*projected_locations)
    x_vals = np.array(x_vals)
    y_vals = np.array(y_vals)

    logging.info("Getting some boundaries")
    # Define the boundaries
    min_x, max_x = x_vals.min(), x_vals.max()
    min_y, max_y = y_vals.min(), y_vals.max()

    logging.info("Making the pixel array...")
    # Create the pixel array (initialized to black)
    heatmap = np.zeros((height, width), dtype=np.uint8)

    locationList = set()


    # Increment the pixel values
    for x, y in projected_locations:
        x_pixel = int((x - min_x) / (max_x - min_x) * (width - 1))
        y_pixel = int((max_y - y) / (max_y - min_y) * (height - 1))  # Flip y-coordinate
        
        # Calculate hue based on location density
        if heatmap[y_pixel, x_pixel] < 250:
            heatmap[y_pixel, x_pixel] += 1
        locationList.add((y_pixel, x_pixel))

    logging.info("Incremented pixel values.")
    max_value = np.max(heatmap)
    print(max_value)
    logging.info(f"Distinct number of values: {len(locationList)}")

    n = 0
    ttl = len(locationList)
    white = 255 #(255,255,255)
    first = time.time()

    print(f"heatmap.dtype: {heatmap.dtype}", file=sys.stderr)
    print(f"heatmap.shape: {heatmap.shape}", file=sys.stderr)
    print(f"heatmap.flags: {heatmap.flags}", file=sys.stderr)

    for location in locationList:
        y, x = location
        if n % 100 == 0:
            if n % 2000 == 0:
                  sys.stderr.write("\n{:4.4f} ".format(100 * n / ttl))
            sys.stderr.write('.')
            sys.stderr.flush()

        n += 1
        heatmap[y, x] = (254 * np.uint32(heatmap[y, x]) / max_value) + 1

    # Convert to image
    logging.info("Converted to image.")

    def row_generator():
        unit = SIZE / 100
        thresh = 0
        n = 0
        for row in range(SIZE):
            if row > thresh:
                if n % 10 == 0:
                  sys.stderr.write("\n{:4d} ".format(n))
                n+= 1
                sys.stderr.write('.')
                sys.stderr.flush()
                thresh += unit

            yield heatmap[row].flatten()

    with open(output_path, 'wb') as f:
        writer = png.Writer(SIZE, SIZE, palette=palette, bitdepth=8, greyscale=False)
        writer.write(f, row_generator())
    sys.stderr.write('\n')

    # Save the image
    #img.save(output_path)
    print(f"Heatmap saved to {output_path}")

    logging.info(f"Heatmap saved to {output_path}")

if __name__ == "__main__":
    file_path = "Timeline.json"
    locations, first_location = load_locations(file_path)
    create_heatmap(locations)

SIZE = 50000
DISTANCE = 15 

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import logging
from PIL import Image
import math
import colorsys

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
                            #print(lat, lng)  # Print statement
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
                        #print(lat, lng)  # Print statement
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
                        #print(lat_start, lng_start)  # Print statement
                    if first_location is not None and abs(lat_end - first_location[0]) <= max_degree_delta and abs(lng_end - first_location[1]) <= max_degree_delta:
                        locations.append((lat_end, lng_end))
                        #print(lat_end, lng_end)  # Print statement
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
    projected_locations = [mercator_projection(lat, lng) for lat, lng in locations]

    # Get x and y values
    x_vals, y_vals = zip(*projected_locations)
    x_vals = np.array(x_vals)
    y_vals = np.array(y_vals)

    # Define the boundaries
    min_x, max_x = x_vals.min(), x_vals.max()
    min_y, max_y = y_vals.min(), y_vals.max()

    # Create the pixel array (initialized to black)
    heatmap = np.zeros((height, width, 3), dtype=np.uint8)

    # Increment the pixel values
    for x, y in projected_locations:
        x_pixel = int((x - min_x) / (max_x - min_x) * (width - 1))
        y_pixel = int((max_y - y) / (max_y - min_y) * (height - 1))  # Flip y-coordinate
        
        # Calculate hue based on location density
        heatmap[y_pixel, x_pixel] += 1

    logging.info("Incremented pixel values.")

    # Normalize the pixel values (logarithmic normalization)
    max_value = np.max(heatmap)
    normalized_heatmap = np.zeros_like(heatmap, dtype=np.float32)
    for y in range(height):
        for x in range(width):
            if max_value > 0 and heatmap[y, x][0] > 0:
                hue = min(360.0, math.log(1 + np.uint64(heatmap[y, x][0])) / math.log(1 + np.uint64(max_value)) * 360.0)
                r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 0.9, 0.9)
                heatmap[y, x] = (int(r * 255), int(g * 255), int(b * 255))
            else:
                heatmap[y, x] = (0, 0, 0) # Black background

    logging.info("Normalized pixel values.")

    # Convert to image
    img = Image.fromarray(heatmap, 'RGB')

    logging.info("Converted to image.")

    # Save the image
    img.save(output_path)
    print(f"Heatmap saved to {output_path}")

    logging.info(f"Heatmap saved to {output_path}")

if __name__ == "__main__":
    file_path = "Timeline.json"
    locations, first_location = load_locations(file_path)
    create_heatmap(locations)

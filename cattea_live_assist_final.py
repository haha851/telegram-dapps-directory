
import cv2
import numpy as np
import os
import time
from collections import defaultdict

# File paths
SCREEN_PATH = "/sdcard/screen.png"
RESULT_PATH = "/sdcard/solution.png"

# Settings
MATCH_THRESHOLD = 0.9
TILE_MIN_SIZE = 50
TILE_MAX_SIZE = 100
TILE_ASPECT_RATIO_MIN = 0.8
TILE_ASPECT_RATIO_MAX = 1.2
OVERLAP_MARGIN = 10  # pixels

def take_screenshot():
    if os.path.exists(SCREEN_PATH):
        os.remove(SCREEN_PATH)
    os.system(f"termux-screencap -f {SCREEN_PATH}")

def average_hash(tile):
    resized = cv2.resize(tile, (8, 8), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    avg = gray.mean()
    return "".join(["1" if px > avg else "0" for px in gray.flatten()])

def detect_tiles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    tiles = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)
        if TILE_MIN_SIZE < w < TILE_MAX_SIZE and TILE_MIN_SIZE < h < TILE_MAX_SIZE and TILE_ASPECT_RATIO_MIN < aspect_ratio < TILE_ASPECT_RATIO_MAX:
            tiles.append((x, y, w, h))

    return sorted(tiles, key=lambda b: (b[1], b[0]))

def filter_visible_tiles(tiles):
    visible = []
    for i, (x1, y1, w1, h1) in enumerate(tiles):
        blocked = False
        for j, (x2, y2, w2, h2) in enumerate(tiles):
            if j == i:
                continue
            if (x1 + OVERLAP_MARGIN < x2 + w2 - OVERLAP_MARGIN and
                x1 + w1 - OVERLAP_MARGIN > x2 + OVERLAP_MARGIN and
                y1 + OVERLAP_MARGIN < y2 + h2 - OVERLAP_MARGIN and
                y1 + h1 - OVERLAP_MARGIN > y2 + OVERLAP_MARGIN and
                y2 < y1):  # the other tile is above this one
                blocked = True
                break
        if not blocked:
            visible.append((x1, y1, w1, h1))
    return visible

def group_similar_tiles(image, tiles):
    tile_groups = defaultdict(list)
    for (x, y, w, h) in tiles:
        tile_img = image[y:y+h, x:x+w]
        hash_val = average_hash(tile_img)
        tile_groups[hash_val].append((x, y, w, h))
    return tile_groups

def draw_matches(image, groups):
    for matches in groups.values():
        if len(matches) >= 3:
            for (x, y, w, h) in matches[:3]:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    return image

def main():
    print("🚀 Cattea Live Assist started. Ctrl+C to stop.")
    while True:
        take_screenshot()
        time.sleep(1.2)

        image = cv2.imread(SCREEN_PATH)
        if image is None:
            print("Waiting for screenshot...")
            time.sleep(2)
            continue

        tiles = detect_tiles(image)
        visible_tiles = filter_visible_tiles(tiles)
        groups = group_similar_tiles(image, visible_tiles)
        output = draw_matches(image.copy(), groups)

        if os.path.exists(RESULT_PATH):
            os.remove(RESULT_PATH)
        cv2.imwrite(RESULT_PATH, output)
        print("✅ Updated solution.png")

        time.sleep(1.5)

if __name__ == "__main__":
    main()

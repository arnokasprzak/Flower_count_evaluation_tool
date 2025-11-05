import os
import math
import rasterio
from rasterio.mask import mask
from rasterio.enums import Resampling
import geopandas as gpd
from shapely.geometry import mapping
import numpy as np
from PIL import Image
from shapely import affinity
from scipy.ndimage import rotate

# === CONFIGURATION ===
gpkg_path = r"C:\Users\akasprzak\OneDrive - ILVO\BELIS\Ortho_data\Ilvo\Small_subplots_L4.gpkg"                               
raster_path = r"C:\Users\akasprzak\OneDrive - ILVO\BELIS\Ortho_data\Ilvo\20250701_1411_L4_20251102_AK_ortho.tif"     
output_dir = r"C:\Users\akasprzak\OneDrive - ILVO\BELIS\Interactive_validation_tool\Subplot_tiles"           
os.makedirs(output_dir, exist_ok=True)

# === READ VECTOR DATA ===
gdf = gpd.read_file(gpkg_path)

with rasterio.open(raster_path) as src:
    # Make sure polygons have the same CRS as the raster
    gdf = gdf.to_crs(src.crs)

    # Loop through each polygon feature
    for i, row in gdf.iterrows():
        poly_id = row.get("id", i)
        split_id = row.get("split_id", 0)
        geom = row.geometry

        # === Step 1: Determine base angle from the longest edge of the polygon ===
        exterior_coords = np.array(geom.exterior.coords)
        max_len = 0
        base_angle = 0
        for j in range(len(exterior_coords) - 1):
            x1, y1 = exterior_coords[j]
            x2, y2 = exterior_coords[j + 1]
            length = math.hypot(x2 - x1, y2 - y1)
            if length > max_len:
                max_len = length
                base_angle = math.degrees(math.atan2(y2 - y1, x2 - x1))

        # === Step 2: Clip the raster using the polygon ===
        out_image, out_transform = mask(src, [mapping(geom)], crop=True)
        
        # Keep only the first 3 bands (RGB)
        if out_image.shape[0] > 3:
            out_image = out_image[:3]

        # === Step 3: Rotate each band to align the polygon base horizontally ===
        rotated_bands = []
        for b in range(out_image.shape[0]):
            band = out_image[b].astype(float)
            band[band == src.nodata] = np.nan
            rotated_band = rotate(band, base_angle, reshape=True, order=1)
            rotated_bands.append(rotated_band)

        # Stack rotated bands back into (height, width, 3)
        rotated_image = np.stack(rotated_bands, axis=-1)

        # === Step 4: Normalize and clean up rotated image ===
        arr = rotated_image.copy()
        arr_min, arr_max = np.nanmin(arr), np.nanmax(arr)
        if arr_max > arr_min:
            arr = (255 * (arr - arr_min) / (arr_max - arr_min)).astype(np.uint8)
        else:
            arr = np.zeros_like(arr, dtype=np.uint8)

        # Replace NaN with 0
        arr = np.nan_to_num(arr, nan=0).astype(np.uint8)

        # === Step 5: Remove empty (black) border ===
        mask_nonzero = np.any(arr > 0, axis=2)  # True where at least one band has data
        rows = np.any(mask_nonzero, axis=1)
        cols = np.any(mask_nonzero, axis=0)

        if np.any(rows) and np.any(cols):
            ymin, ymax = np.where(rows)[0][[0, -1]]
            xmin, xmax = np.where(cols)[0][[0, -1]]
            arr = arr[ymin:ymax + 1, xmin:xmax + 1, :]

        img = Image.fromarray(arr, mode="RGB")
        out_name = f"{poly_id}_{split_id}.jpg"
        img.save(os.path.join(output_dir, out_name), "JPEG", quality=95)
        print(f"Saved cropped RGB tile: {out_name}")

        



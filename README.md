# Photo2GeoJSON

**A QGIS plugin that turns a folder of geotagged photos into a styled GeoJSON point layer — with camera direction, thumbnail map tips, and deep DJI drone metadata support.**

Point QGIS at a folder of JPEGs and get an instant map of where every photo was taken, which way the camera was facing, and (for DJI drones) the full flight metadata — not just the basic EXIF that most tools stop at.

> Made by [ARENARIA](https://arenaria.pl) · QGIS 3.16+

---

## Features

- **Folder → map in one click.** Scan a folder of JPEG photos (optionally recursive) and get a GeoJSON point layer added straight to your project.
- **Standard EXIF GPS** from any camera or phone (via `exifread`).
- **Deep DJI drone support — reads the raw XMP block, not just EXIF.** Works with DJI Mavic, Phantom 4 Pro, and Phantom 4 **RTK**. Extracts:
  - gimbal yaw → **azimuth** (camera compass direction), gimbal pitch, flight yaw
  - absolute altitude
  - RTK **fix flag** and position standard deviations (lon/lat/height)
  - flight speeds (X/Y/Z)
  - handles the real Phantom 4 RTK tag typo (`GpsLongtitude`, extra “t”) so RTK images don’t silently fail.
- **Direction-aware symbology.** Each point is drawn as a rotated arrow + camera marker pointing the way the shot was taken (azimuth-driven).
- **Thumbnail map tips.** Hover a point to preview the photo; the point also carries an action to open the original file.
- **Automatic labels** from the filename and a **timestamped layer name** so repeated runs don’t clash.
- **Bilingual UI (English / Polish)** — automatically selected by your QGIS language.
- **Non-blocking.** Scanning runs on a worker thread; a sidecar `.qml` style is written next to the GeoJSON.

## Output fields

Each point carries:

| Field | Description |
|---|---|
| `filepath`, `filename` | Full path and clean name (no extension) of the source photo |
| `latitude`, `longitude`, `altitude` | Coordinates (WGS84) and altitude (m) |
| `azimuth`, `north` | Camera direction (0–360°) and its reference (`T` = true for DJI) |
| `gimbal_pitch`, `flight_yaw` | DJI only — gimbal pitch and aircraft heading |
| `rtk_flag`, `rtk_std_lon`, `rtk_std_lat`, `rtk_std_hgt` | DJI RTK only — fix flag and position std. deviations |
| `speed_x`, `speed_y`, `speed_z` | DJI only — flight speed components (m/s) |
| `gps_date`, `img_date` | GPS date and image capture timestamp |
| `source` | `EXIF`, `DJI`, or `DJI-RTK` |

## Requirements

- **QGIS 3.16 or newer**
- Python package **`exifread`** — this is an external dependency that is **not** shipped with QGIS. Install it into the QGIS Python environment:
  - **Windows (OSGeo4W):** open the *OSGeo4W Shell* and run `pip install exifread`
  - **Linux/macOS:** `pip install exifread` in the Python environment QGIS uses
  - After installing, restart QGIS.

## Installation

**From ZIP (now):**
1. Download the latest release ZIP.
2. In QGIS: *Plugins → Manage and Install Plugins… → Install from ZIP* → select the file.
3. Enable **Photo2GeoJSON**.

**From the QGIS Official Plugin Repository:** _(planned — pending approval)_ search “Photo2GeoJSON” in the Plugin Manager.

## Usage

1. Click the **Photo2GeoJSON** toolbar icon (or *Plugins → Photo2GeoJSON*).
2. Choose the **folder of JPEG photos** (tick *recursive* to include sub-folders).
3. Pick the **output `.geojson`** path and a **layer name**.
4. Click **Create layer** — points appear on the map with direction arrows. Hover for thumbnails; click a point’s action to open the photo.

## How it works

- Standard EXIF GPS is read with `exifread` and converted from DMS to decimal degrees.
- DJI metadata is parsed directly from the `drone-dji:` namespace inside the photo’s XMP packet (read from the file’s first 128 KB), which is where DJI stores gimbal/flight/RTK data that standard EXIF readers miss.
- Azimuth comes from `GimbalYawDegree` (DJI) or `GPSImgDirection` (standard EXIF).
- Symbology, map tips, labels and the photo-open action are applied from an embedded QML style (uses QGIS’ built-in `arrows/Arrow_06.svg` and `gpsicons/camera.svg`, so nothing extra to install).

## Background

Photo2GeoJSON grew out of ARENARIA’s field nature-documentation work — we needed a dependable way to map large sets of geotagged photos, including DJI drone shots whose most useful data hides beyond standard EXIF. The DJI/RTK extraction started as a bit of tinkering that turned out genuinely useful for our surveys.

It was loosely inspired by the old, now-defunct *photo2shp* plugin, but is an **independent implementation written from scratch — it shares no code with it** and took a different path entirely.

## Known limitations / roadmap

- Input is **JPEG** only.
- `exifread` must be installed manually (see Requirements) — bundling is under consideration.

## License

Released under the **GNU General Public License v3.0** — see [`LICENSE`](LICENSE). _(QGIS core is GPLv2-or-later; GPLv3 is compatible.)_

## Credits

Created by **Andrzej Rodziewicz — Arenaria Sp. z o.o.**, with development assistance from **Claude (Anthropic)**.

ARENARIA — nature documentation & GIS for agri-environmental programmes · [arenaria.pl](https://arenaria.pl)

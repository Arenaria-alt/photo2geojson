# -*- coding: utf-8 -*-
import os
import re
from fractions import Fraction

# exifread is an external dependency (not shipped with QGIS). Import it
# lazily so the plugin still loads if it is missing; the dialog checks
# EXIFREAD_AVAILABLE and shows a friendly "please install" message instead
# of crashing QGIS on load.
try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    exifread = None
    EXIFREAD_AVAILABLE = False


def _rational_to_float(value):
    try:
        if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
            if value.denominator == 0:
                return 0.0
            return float(value.numerator) / float(value.denominator)
        s = str(value)
        if '/' in s:
            f = Fraction(s)
            return float(f)
        return float(s)
    except Exception:
        return 0.0


def _dms_to_decimal(dms_values, ref):
    try:
        vals = dms_values.values if hasattr(dms_values, 'values') else dms_values
        deg = _rational_to_float(vals[0])
        mn  = _rational_to_float(vals[1])
        sec = _rational_to_float(vals[2])
        decimal = deg + mn / 60.0 + sec / 3600.0
        ref_str = str(ref).strip().upper()
        if ref_str in ('S', 'W'):
            decimal = -decimal
        return round(decimal, 8)
    except Exception:
        return None


def _yaw_to_azimuth(yaw_str):
    """Convert DJI yaw (-180..+180) to standard azimuth (0..360)."""
    try:
        yaw = float(yaw_str)
        return round(yaw % 360, 1)
    except Exception:
        return None


def _extract_xmp_dji(filepath):
    """
    Read raw XMP block from JPEG and extract DJI metadata.
    Handles standard DJI (Mavic/Phantom4Pro) and RTK variants.

    Notable quirk: Phantom 4 RTK has a typo in the tag name:
    'GpsLongtitude' (extra 't') instead of 'GpsLongitude'.
    """
    result = {
        'latitude':    None,
        'longitude':   None,
        'altitude':    None,
        'gimbal_yaw':  None,
        'gimbal_pitch': None,
        'flight_yaw':  None,
        'rtk_flag':    None,
        'rtk_std_lon': None,
        'rtk_std_lat': None,
        'rtk_std_hgt': None,
        'speed_x':     None,
        'speed_y':     None,
        'speed_z':     None,
    }
    try:
        with open(filepath, 'rb') as f:
            data = f.read(131072)

        xmp_start = data.find(b'<x:xmpmeta')
        xmp_end   = data.find(b'</x:xmpmeta')
        if xmp_start == -1 or xmp_end == -1:
            return result

        xmp = data[xmp_start:xmp_end + 12].decode('utf-8', errors='ignore')

        def _attr(name):
            m = re.search(r'drone-dji:' + name + r'=["\']([^"\']+)["\']', xmp)
            return m.group(1).strip() if m else None

        def _flt(val, decimals=8):
            try:
                return round(float(val), decimals) if val is not None else None
            except Exception:
                return None

        raw_lat = _attr('GpsLatitude')
        # Ph4 RTK has typo: GpsLongtitude (extra 't') — check both
        raw_lon = _attr('GpsLongitude') or _attr('GpsLongtitude')
        raw_alt = _attr('AbsoluteAltitude')
        raw_gy  = _attr('GimbalYawDegree')
        raw_gp  = _attr('GimbalPitchDegree')
        raw_fy  = _attr('FlightYawDegree')

        result['latitude']    = _flt(raw_lat)
        result['longitude']   = _flt(raw_lon)
        result['altitude']    = _flt(raw_alt, 2)
        result['gimbal_yaw']  = _yaw_to_azimuth(raw_gy)
        result['gimbal_pitch'] = _flt(raw_gp, 1)
        result['flight_yaw']  = _yaw_to_azimuth(raw_fy)

        # RTK precision fields (only present in RTK models)
        result['rtk_flag']    = _attr('RtkFlag')
        result['rtk_std_lon'] = _flt(_attr('RtkStdLon'), 5)
        result['rtk_std_lat'] = _flt(_attr('RtkStdLat'), 5)
        result['rtk_std_hgt'] = _flt(_attr('RtkStdHgt'), 5)

        # Flight speed (m/s)
        result['speed_x']     = _flt(_attr('FlightXSpeed'), 2)
        result['speed_y']     = _flt(_attr('FlightYSpeed'), 2)
        result['speed_z']     = _flt(_attr('FlightZSpeed'), 2)

    except (OSError, ValueError, TypeError, re.error):
        # Unreadable file or malformed XMP block: leave DJI/RTK fields
        # as None so the photo is still usable via standard EXIF.
        return result

    return result


def extract_exif(filepath):
    """
    Extract GPS and date info from a JPEG.
    Supports standard EXIF (cameras), DJI standard and DJI RTK drones.

    Returns dict or None if no GPS data found.
    """
    try:
        with open(filepath, 'rb') as f:
            tags = exifread.process_file(f, details=False)
    except Exception:
        return None

    # Standard EXIF GPS
    lat_tag = tags.get('GPS GPSLatitude')
    lat_ref = tags.get('GPS GPSLatitudeRef')
    lon_tag = tags.get('GPS GPSLongitude')
    lon_ref = tags.get('GPS GPSLongitudeRef')

    lat = _dms_to_decimal(lat_tag, lat_ref) if all([lat_tag, lat_ref, lon_tag, lon_ref]) else None
    lon = _dms_to_decimal(lon_tag, lon_ref) if all([lat_tag, lat_ref, lon_tag, lon_ref]) else None

    # DJI XMP block
    xmp = _extract_xmp_dji(filepath)
    is_dji = xmp['gimbal_yaw'] is not None or xmp['flight_yaw'] is not None or xmp['rtk_flag'] is not None

    # Coordinates: prefer standard EXIF, fall back to DJI XMP
    if lat is None and xmp['latitude'] is not None:
        lat = xmp['latitude']
        lon = xmp['longitude']

    if lat is None or lon is None:
        return None

    # Altitude
    alt = 0.0
    alt_tag = tags.get('GPS GPSAltitude')
    if alt_tag:
        alt = round(_rational_to_float(alt_tag.values[0] if hasattr(alt_tag, 'values') else alt_tag), 2)
        alt_ref = tags.get('GPS GPSAltitudeRef')
        if alt_ref and str(alt_ref) == '1':
            alt = -alt
    elif xmp['altitude'] is not None:
        alt = xmp['altitude']

    # Azimuth
    azimuth = None
    north   = None
    if is_dji:
        azimuth = xmp['gimbal_yaw']
        north   = 'T'
    else:
        dir_tag = tags.get('GPS GPSImgDirection')
        if dir_tag:
            azimuth = round(_rational_to_float(dir_tag.values[0] if hasattr(dir_tag, 'values') else dir_tag), 1)
        north_tag = tags.get('GPS GPSImgDirectionRef')
        if north_tag:
            north = str(north_tag).strip()

    # Dates
    gps_date = None
    gps_date_tag = tags.get('GPS GPSDate')
    if gps_date_tag:
        gps_date = str(gps_date_tag).replace(':', '-')

    img_date = None
    for dt_key in ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime'):
        dt_tag = tags.get(dt_key)
        if dt_tag:
            img_date = str(dt_tag)
            break

    # Source tag
    if is_dji:
        source = 'DJI-RTK' if xmp['rtk_flag'] is not None else 'DJI'
    else:
        source = 'EXIF'

    fname = os.path.splitext(os.path.basename(filepath))[0]

    return {
        'filepath':    filepath.replace('\\', '/'),
        'filename':    fname,
        'longitude':   lon,
        'latitude':    lat,
        'altitude':    alt,
        'north':       north,
        'azimuth':     azimuth,
        'gimbal_pitch': xmp['gimbal_pitch'] if is_dji else None,
        'flight_yaw':  xmp['flight_yaw'] if is_dji else None,
        'rtk_flag':    xmp['rtk_flag'],
        'rtk_std_lon': xmp['rtk_std_lon'],
        'rtk_std_lat': xmp['rtk_std_lat'],
        'rtk_std_hgt': xmp['rtk_std_hgt'],
        'speed_x':     xmp['speed_x'],
        'speed_y':     xmp['speed_y'],
        'speed_z':     xmp['speed_z'],
        'gps_date':    gps_date,
        'img_date':    img_date,
        'source':      source,
    }


def scan_folder(folder, recursive=False):
    """Scan folder for JPEG files and extract EXIF data."""
    results = []
    extensions = {'.jpg', '.jpeg', '.JPG', '.JPEG'}

    if recursive:
        for root, dirs, files in os.walk(folder):
            for fname in files:
                if os.path.splitext(fname)[1] in extensions:
                    fp = os.path.join(root, fname)
                    data = extract_exif(fp)
                    if data:
                        results.append(data)
    else:
        for fname in os.listdir(folder):
            if os.path.splitext(fname)[1] in extensions:
                fp = os.path.join(folder, fname)
                data = extract_exif(fp)
                if data:
                    results.append(data)

    return results

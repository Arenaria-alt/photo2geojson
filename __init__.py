# -*- coding: utf-8 -*-
def classFactory(iface):
    from .photo2geojson import Photo2GeoJSON
    return Photo2GeoJSON(iface)

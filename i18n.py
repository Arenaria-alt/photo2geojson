# -*- coding: utf-8 -*-
"""
Lightweight bilingual (English / Polish) string table for Photo2GeoJSON.

The language is chosen automatically from the QGIS UI locale:
Polish when QGIS runs in Polish, English otherwise (default for everyone else).

Usage:
    from .i18n import tr
    tr('btn_run')                       -> localized string
    tr('status_found', n=12)            -> string with .format() kwargs
"""

_STRINGS = {
    # window / groups
    'window_title':   {'en': 'Photo2GeoJSON',                         'pl': 'Photo2GeoJSON'},
    'grp_input':      {'en': 'Photo folder (JPEG)',                   'pl': 'Folder ze zdjęciami (JPEG)'},
    'grp_output':     {'en': 'Output GeoJSON file',                   'pl': 'Plik wyjściowy GeoJSON'},
    # inputs
    'ph_input':       {'en': 'Choose a folder…',                     'pl': 'Wybierz folder…'},
    'chk_recursive':  {'en': 'Search sub-folders recursively',        'pl': 'Przeszukuj podfoldery rekurencyjnie'},
    'ph_output':      {'en': 'Save as .geojson …',                   'pl': 'Zapisz jako .geojson …'},
    'lbl_name':       {'en': 'Layer name:',                           'pl': 'Nazwa warstwy:'},
    # buttons
    'btn_run':        {'en': '▶  Create layer',                      'pl': '▶  Utwórz warstwę'},
    'btn_close':      {'en': 'Close',                                 'pl': 'Zamknij'},
    # dialogs / file pickers
    'dlg_pick_input': {'en': 'Choose photo folder',                   'pl': 'Wybierz folder ze zdjęciami'},
    'dlg_save':       {'en': 'Save GeoJSON',                          'pl': 'Zapisz GeoJSON'},
    'filter_geojson': {'en': 'GeoJSON (*.geojson);;All files (*)',    'pl': 'GeoJSON (*.geojson);;Wszystkie pliki (*)'},
    # messages
    'msg_error':      {'en': 'Error',                                 'pl': 'Błąd'},
    'err_folder':     {'en': 'Please provide a valid photo folder.',  'pl': 'Podaj prawidłowy folder ze zdjęciami.'},
    'err_output':     {'en': 'Please provide an output file path.',   'pl': 'Podaj ścieżkę do pliku wyjściowego.'},
    'status_scanning':{'en': 'Scanning photos…',                     'pl': 'Skanowanie zdjęć…'},
    'status_none':    {'en': 'No photos with GPS data found.',        'pl': 'Nie znaleziono zdjęć z danymi GPS.'},
    'title_nodata':   {'en': 'No data',                               'pl': 'Brak danych'},
    'msg_nodata':     {'en': 'No JPEG photos with GPS EXIF data were found in the selected folder.',
                       'pl': 'Nie znaleziono żadnych zdjęć JPEG z danymi GPS EXIF w wybranym folderze.'},
    'status_found':   {'en': 'Found {n} photos. Building layer…',    'pl': 'Znaleziono {n} zdjęć. Tworzenie warstwy…'},
    'status_done':    {'en': '✓ Layer "{name}" added to the project ({n} points).',
                       'pl': '✓ Warstwa „{name}” dodana do projektu ({n} punktów).'},
    'err_loadlayer':  {'en': 'Failed to load the layer from the GeoJSON file.',
                       'pl': 'Nie udało się załadować warstwy z pliku GeoJSON.'},
    'status_error':   {'en': 'Error: {msg}',                          'pl': 'Błąd: {msg}'},
}


def _lang():
    """Return 'pl' if QGIS runs in Polish, otherwise 'en'."""
    loc = ''
    try:
        from qgis.core import QgsSettings
        loc = QgsSettings().value('locale/userLocale', '') or ''
    except Exception:
        loc = ''
    if not loc:
        try:
            from qgis.PyQt.QtCore import QLocale
            loc = QLocale.system().name()
        except Exception:
            loc = ''
    return 'pl' if str(loc).lower().startswith('pl') else 'en'


def tr(key, **kwargs):
    entry = _STRINGS.get(key, {})
    text = entry.get(_lang()) or entry.get('en') or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text

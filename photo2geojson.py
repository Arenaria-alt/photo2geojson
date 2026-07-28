# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .dialog import Photo2GeoJSONDialog

class Photo2GeoJSON:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dlg = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icons', 'camera.png')
        self.action = QAction(
            QIcon(icon_path),
            'Photo2GeoJSON',
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('&Photo2GeoJSON', self.action)

    def unload(self):
        self.iface.removePluginMenu('&Photo2GeoJSON', self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if not self.dlg:
            self.dlg = Photo2GeoJSONDialog(self.iface)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

# -*- coding: utf-8 -*-
import os
from datetime import datetime
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QSizePolicy
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtGui import QFont

from .exif_utils import scan_folder
from .layer_builder import save_and_load_layer
from .i18n import tr


# ── Worker thread ─────────────────────────────────────────────────────────────
class ScanWorker(QThread):
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, folder, recursive):
        super().__init__()
        self.folder    = folder
        self.recursive = recursive

    def run(self):
        try:
            data = scan_folder(self.folder, self.recursive)
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))


# ── Dialog ────────────────────────────────────────────────────────────────────
class Photo2GeoJSONDialog(QDialog):
    def __init__(self, iface, parent=None):
        super().__init__(parent or iface.mainWindow())
        self.iface  = iface
        self.worker = None
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setWindowTitle(tr('window_title'))
        self.setMinimumWidth(520)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        root = QVBoxLayout(self)
        root.setSpacing(10)

        # ── Input folder ──────────────────────────────────────────────────────
        grp_in = QGroupBox(tr('grp_input'))
        lay_in = QVBoxLayout(grp_in)

        row_in = QHBoxLayout()
        self.le_input = QLineEdit()
        self.le_input.setPlaceholderText(tr('ph_input'))
        btn_in = QPushButton('…')
        btn_in.setFixedWidth(32)
        btn_in.clicked.connect(self._browse_input)
        row_in.addWidget(self.le_input)
        row_in.addWidget(btn_in)

        self.chk_recursive = QCheckBox(tr('chk_recursive'))
        lay_in.addLayout(row_in)
        lay_in.addWidget(self.chk_recursive)
        root.addWidget(grp_in)

        # ── Output file ───────────────────────────────────────────────────────
        grp_out = QGroupBox(tr('grp_output'))
        lay_out = QVBoxLayout(grp_out)

        row_out = QHBoxLayout()
        self.le_output = QLineEdit()
        self.le_output.setPlaceholderText(tr('ph_output'))
        btn_out = QPushButton('…')
        btn_out.setFixedWidth(32)
        btn_out.clicked.connect(self._browse_output)
        row_out.addWidget(self.le_output)
        row_out.addWidget(btn_out)

        row_name = QHBoxLayout()
        lbl_name = QLabel(tr('lbl_name'))
        lbl_name.setFixedWidth(100)
        self.le_name = QLineEdit('photos')
        row_name.addWidget(lbl_name)
        row_name.addWidget(self.le_name)

        lay_out.addLayout(row_out)
        lay_out.addLayout(row_name)
        root.addWidget(grp_out)

        # ── Progress ──────────────────────────────────────────────────────────
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate spinner
        self.progress.setVisible(False)
        root.addWidget(self.progress)

        self.lbl_status = QLabel('')
        self.lbl_status.setAlignment(Qt.AlignCenter)
        small = QFont()
        small.setPointSize(9)
        self.lbl_status.setFont(small)
        root.addWidget(self.lbl_status)

        # ── Buttons ───────────────────────────────────────────────────────────
        row_btn = QHBoxLayout()
        self.btn_run   = QPushButton(tr('btn_run'))
        self.btn_close = QPushButton(tr('btn_close'))
        self.btn_run.setDefault(True)
        self.btn_run.clicked.connect(self._run)
        self.btn_close.clicked.connect(self.close)
        row_btn.addStretch()
        row_btn.addWidget(self.btn_run)
        row_btn.addWidget(self.btn_close)
        root.addLayout(row_btn)

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _browse_input(self):
        folder = QFileDialog.getExistingDirectory(
            self, tr('dlg_pick_input'), self.le_input.text() or ''
        )
        if folder:
            self.le_input.setText(folder)
            if not self.le_output.text():
                self.le_output.setText(os.path.join(folder, 'photos.geojson'))

    def _browse_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self, tr('dlg_save'), self.le_output.text() or '',
            tr('filter_geojson')
        )
        if path:
            if not path.lower().endswith('.geojson'):
                path += '.geojson'
            self.le_output.setText(path)

    def _run(self):
        folder = self.le_input.text().strip()
        out    = self.le_output.text().strip()
        name   = self.le_name.text().strip() or 'photos'

        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, tr('msg_error'), tr('err_folder'))
            return
        if not out:
            QMessageBox.warning(self, tr('msg_error'), tr('err_output'))
            return

        self._set_busy(True)
        self.lbl_status.setText(tr('status_scanning'))

        self.worker = ScanWorker(folder, self.chk_recursive.isChecked())
        self.worker.finished.connect(lambda data: self._on_scan_done(data, out, name))
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_scan_done(self, data, out_path, layer_name):
        self._set_busy(False)
        if not data:
            self.lbl_status.setText(tr('status_none'))
            QMessageBox.information(self, tr('title_nodata'), tr('msg_nodata'))
            return

        # Append timestamp: photos_20260603_2012
        ts = datetime.now().strftime('%Y%m%d_%H%M')
        layer_name_ts = f'{layer_name}_{ts}'

        self.lbl_status.setText(tr('status_found', n=len(data)))
        try:
            layer = save_and_load_layer(data, out_path, layer_name_ts)
            if layer:
                self.lbl_status.setText(tr('status_done', name=layer_name_ts, n=len(data)))
            else:
                self._on_error(tr('err_loadlayer'))
        except Exception as e:
            self._on_error(str(e))

    def _on_error(self, msg):
        self._set_busy(False)
        self.lbl_status.setText(tr('status_error', msg=msg))
        QMessageBox.critical(self, tr('msg_error'), msg)

    def _set_busy(self, busy):
        self.btn_run.setEnabled(not busy)
        self.progress.setVisible(busy)

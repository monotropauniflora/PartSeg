import json
import logging
import os
import re

import tifffile as tif
import numpy as np
import SimpleITK as sitk
import appdirs
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QFileDialog, QMessageBox, QCheckBox, QComboBox, QStackedLayout

from common_gui.channel_control import ChannelControl
from project_utils.algorithms_description import InteractiveAlgorithmSettingsWidget
from project_utils.global_settings import static_file_folder
from .partseg_settings import PartSettings, load_project, save_project,save_labeled_image
from .image_view import RawImageView, ResultImageView
from .algorithm_description import part_algorithm_dict

app_name = "PartSeg2"
app_lab = "LFSG"
config_folder = appdirs.user_data_dir(app_name, app_lab)


class Options(QWidget):
    def __init__(self, settings: PartSettings, channel_control1: ChannelControl, channel_control2: ChannelControl,
                 left_panel: RawImageView):
        super().__init__()
        self._settings = settings
        self.left_panel = left_panel
        self._ch_control1 = channel_control1
        self._ch_control2 = channel_control2
        self.synchronize = QCheckBox("Synchronize views")
        self.synchronize.stateChanged.connect(self.synchronize_change)
        self.off_left = QCheckBox("Hide left panel")
        self.off_left.stateChanged.connect(self.hide_left_panel)
        self._ch_control2.coloring_update.connect(self.control2_change)
        self.stack_layout = QStackedLayout()
        self.algorithm_choose = QComboBox()
        self.interactive_use = QCheckBox("Interactive use")
        self.execute_btn = QPushButton("Execute")
        self.execute_btn.clicked.connect(self.execute_algorithm)
        self.interactive_use.stateChanged.connect(self.execute_btn.setDisabled)
        self.interactive_use.stateChanged.connect(self.interactive_change)
        widgets_list = []
        for name, val in part_algorithm_dict.items():
            self.algorithm_choose.addItem(name)
            widget = InteractiveAlgorithmSettingsWidget(settings, name, *val)
            widgets_list.append(widget)
            widget.algorithm.execution_done.connect(self.execution_done)
            #widget.algorithm.progress_signal.connect(self.progress_info)
            self.stack_layout.addWidget(widget)

        self.label = QLabel()
        layout = QVBoxLayout()
        layout2 = QHBoxLayout()
        layout2.setSpacing(1)
        layout2.setContentsMargins(0, 0, 0, 0)
        layout3 = QHBoxLayout()
        layout3.setContentsMargins(0, 0, 0, 0)
        layout.setContentsMargins(0,0,0,0)
        layout3.addWidget(self.interactive_use)
        layout3.addWidget(self.execute_btn)
        layout.addLayout(layout3)
        layout.addWidget(self.algorithm_choose)
        layout.addLayout(self.stack_layout)
        layout.addWidget(self.label, 1)
        layout2.addWidget(self.synchronize)
        layout2.addWidget(self.off_left)
        layout.addLayout(layout2)
        layout.addWidget(self._ch_control2)
        layout.addWidget(self._ch_control1)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.algorithm_choose.currentIndexChanged.connect(self.stack_layout.setCurrentIndex)
        self.algorithm_choose.currentIndexChanged.connect(self.algorithm_change)

    @property
    def segmentation(self):
        return self._settings.segmentation

    @segmentation.setter
    def segmentation(self, val):
        self._settings.segmentation = val

    def image_changed(self):
        self.segmentation = None

    @property
    def interactive(self):
        return self.interactive_use.isChecked()

    def synchronize_change(self, val):
        if val:
            self._ch_control1.set_temp_name(self._ch_control2._name)
        else:
            self._ch_control1.set_temp_name()
        self._ch_control1.setHidden(val)

    def control2_change(self):
        if self.synchronize.isChecked():
            print("AAAAAAA")
            self._ch_control1.refresh_info()

    def hide_left_panel(self, val):
        self._ch_control1.setHidden(val)
        self.left_panel.setHidden(val)
        self.synchronize.setChecked(False)

    def interactive_change(self, val):
        if val:
            self.execute_algorithm()

    def algorithm_change(self):
        if self.interactive:
            self.execute_algorithm()

    def execute_algorithm(self):
        widget: InteractiveAlgorithmSettingsWidget = self.stack_layout.currentWidget()
        widget.execute()

    def execution_done(self, segmentation):
        self.segmentation = segmentation

class MainMenu(QWidget):
    def __init__(self, settings: PartSettings):
        super().__init__()
        self._settings = settings
        self.open_btn = QPushButton("Open")
        self.save_btn = QPushButton("Save")
        self.advanced_btn = QPushButton("Advanced")
        self.interpolate_btn = QPushButton("Interpolate")

        layout = QHBoxLayout()
        layout.addWidget(self.open_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.advanced_btn)
        layout.addWidget(self.interpolate_btn)
        self.setLayout(layout)

        self.open_btn.clicked.connect(self.load_data)

    def load_data(self):
        try:
            dial = QFileDialog(self, "Load data")
            dial.setDirectory(self._settings.get("io.open_directory", ""))
            dial.setFileMode(QFileDialog.ExistingFile)
            filters = ["raw image (*.tiff *.tif *.lsm)", "image with mask (*.tiff *.tif *.lsm)",
                       "mask to image (*.tiff *.tif *.lsm)", "image with current mask (*.tiff *.tif *.lsm)",
                       "saved project (*.tgz *.tbz2 *.gz *.bz2)", "Profiles (*.json)"]
            # dial.setFilters(filters)
            dial.setNameFilters(filters)
            dial.selectNameFilter(self._settings.get("io.open_filter", filters[0]))
            if dial.exec_():
                file_path = str(dial.selectedFiles()[0])
                self._settings.set("io.open_directory", os.path.dirname(str(file_path)))
                selected_filter = str(dial.selectedNameFilter())
                self._settings.set("io.open_filter", selected_filter)
                logging.debug("open file: {}, filter {}".format(file_path, selected_filter))
                # TODO maybe something better. Now main window have to be parent
                if selected_filter == "raw image (*.tiff *.tif *.lsm)":
                    im = tif.imread(file_path)
                    self._settings.image = im, file_path
                elif selected_filter == "mask to image (*.tiff *.tif *.lsm)":
                    im = tif.imread(file_path)
                    self._settings.mask = im
                elif selected_filter == "image with current mask (*.tiff *.tif *.lsm)":
                    mask = self._settings
                    im = tif.imread(file_path)
                    self._settings.image = im, file_path
                    self._settings.mask = mask
                elif selected_filter == "image with mask (*.tiff *.tif *.lsm)":
                    extension = os.path.splitext(file_path)
                    if extension == ".json":
                        with open(file_path) as ff:
                            info_dict = json.load(ff)
                        image = tif.imread(info_dict["image"])
                        mask = tif.imread(info_dict["mask"])
                        self._settings.image = image, info_dict["image"]
                        self._settings.mask = mask
                    else:
                        image = tif.imread(file_path)
                        org_name = os.path.basename(file_path)
                        mask_dial = QFileDialog(self, "Load mask for {}".format(org_name))
                        filters = ["mask (*.tiff *.tif *.lsm)"]
                        mask_dial.setNameFilters(filters)
                        if mask_dial.exec_():
                            mask = tif.imread(mask_dial.selectedFiles()[0])
                            self._settings.image = image, file_path
                            self._settings.mask = mask
                elif selected_filter == "saved project (*.tgz *.tbz2 *.gz *.bz2)":
                    load_project(file_path, self._settings)
                    # self.segment.threshold_updated()
                elif selected_filter == "Profiles (*.json)":
                    self._settings.load_profiles(file_path)
                else:
                    # noinspection PyCallByClass
                    _ = QMessageBox.warning(self, "Load error", "Function do not implemented yet")
                    return
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Open error", "Exception occurred {}".format(e))

    def save_file(self):
        try:
            dial = QFileDialog(self, "Save data")
            dial.setDirectory(self._settings.get("io.save_directory", self._settings.get("io.open_directory", "")))
            dial.setFileMode(QFileDialog.AnyFile)
            filters = ["Project (*.tgz *.tbz2 *.gz *.bz2)", "Labeled image (*.tif)", "Mask in tiff (*.tif)",
                       "Mask for itk-snap (*.img)", "Data for chimera (*.cmap)", "Image (*.tiff)", "Profiles (*.json)",
                       "Segmented data in xyz (*.xyz)"]
            dial.setAcceptMode(QFileDialog.AcceptSave)
            dial.setNameFilters(filters)
            default_name = os.path.splitext(os.path.basename(self._settings.file_path))[0]
            dial.selectFile(default_name)
            dial.selectNameFilter(self._settings.get("io.save_filter", ""))
            if dial.exec_():
                file_path = str(dial.selectedFiles()[0])
                selected_filter = str(dial.selectedNameFilter())
                self._settings.set("io.save_filter", selected_filter)
                self._settings.set("io.save_directory", os.path.dirname(file_path))
                if os.path.splitext(file_path)[1] == '':
                    ext = re.search(r'\(\*(\.\w+)', selected_filter).group(1)
                    file_path += ext
                    if os.path.exists(file_path):
                        # noinspection PyCallByClass
                        ret = QMessageBox.warning(self, "File exist", os.path.basename(file_path) +
                                                  " already exists.\nDo you want to replace it?",
                                                  QMessageBox.No | QMessageBox.Yes)
                        if ret == QMessageBox.No:
                            self.save_file()
                            return

                if selected_filter == "Project (*.tgz *.tbz2 *.gz *.bz2)":
                    save_project(file_path, self.settings, self.segment)

                elif selected_filter == "Labeled image (*.tif)":
                    save_labeled_image(file_path, self._settings)

                elif selected_filter == "Mask in tiff (*.tif)":
                    segmentation = self._settings.segmentation
                    segmentation = np.array(segmentation > 0).astype(np.uint8)
                    tif.imsave(file_path, segmentation)
                elif selected_filter == "Mask for itk-snap (*.img)":
                    segmentation = sitk.GetImageFromArray(self.segment.get_segmentation())
                    sitk.WriteImage(segmentation, file_path)
                elif selected_filter == "Data for chimera (*.cmap)":
                    if not np.any(self.segment.get_segmentation()):
                        QMessageBox.warning(self, "No object", "There is no component to export to cmap")
                        return
                    ob = CmapSave(file_path, self.settings, self.segment)
                    ob.exec_()
                elif selected_filter == "Image (*.tiff)":
                    image = self.settings.image
                    tif.imsave(file_path, image)
                elif selected_filter == "Profiles (*.json)":
                    self.settings.dump_profiles(file_path)
                elif selected_filter == "Segmented data in xyz (*.xyz)":
                    save_to_xyz(file_path, self.settings, self.segment)
                else:
                    # noinspection PyCallByClass
                    _ = QMessageBox.critical(self, "Save error", "Option unknown")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Open error", "Exception occurred {}".format(e))


class MainWindow(QMainWindow):
    def __init__(self, title):
        super(MainWindow, self).__init__()
        self.setWindowTitle(title)
        self.title = title
        self.setMinimumWidth(600)
        self.settings = PartSettings()
        if os.path.exists(os.path.join(config_folder, "settings.json")):
            self.settings.load(os.path.join(config_folder, "settings.json"))
        self.main_menu = MainMenu(self.settings)
        self.channel_control1 = ChannelControl(self.settings, name="raw_control", text="Left panel:")
        self.channel_control2 = ChannelControl(self.settings, name="result_control", text="Right panel:")
        self.raw_image = RawImageView(self.settings, self.channel_control1)
        self.result_image = ResultImageView(self.settings, self.channel_control2)
        self.info_text = QLabel()
        self.raw_image.text_info_change.connect(self.info_text.setText)
        self.result_image.text_info_change.connect(self.info_text.setText)
        # image_view_control = self.image_view.get_control_view()
        self.options_panel = Options(self.settings, self.channel_control1, self.channel_control2, self.raw_image)
        # self.main_menu.image_loaded.connect(self.image_read)
        self.settings.image_changed.connect(self.image_read)

        im = tif.imread(os.path.join(static_file_folder, 'initial_images', "clean_segment.tiff"))
        self.settings.image = im

        icon = QIcon(os.path.join(static_file_folder, 'icons', "icon.png"))
        self.setWindowIcon(icon)

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.addWidget(self.main_menu, 0, 0, 1, 4)
        layout.addWidget(self.info_text, 1, 0, 1, 2, Qt.AlignHCenter)  # , 0, 4)
        layout.addWidget(self.raw_image, 2, 0)  # , 0, 0)
        layout.addWidget(self.result_image, 2, 1)  # , 0, 0)
        layout.addWidget(self.options_panel, 2, 2)  # , 0, 0)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        try:
            geometry = self.settings.get_from_profile("main_window_geometry")
            self.restoreGeometry(QByteArray.fromHex(bytes(geometry, 'ascii')))
        except KeyError:
            pass


    def image_read(self):
        print("buka1", self.settings.image.shape, self.sender())
        self.raw_image.set_image(self.settings.image)
        self.result_image.set_image(self.settings.image)
        self.setWindowTitle(f"PartSeg: {self.settings.image_path}")

    def closeEvent(self, _):
        # print(self.settings.dump_view_profiles())
        # print(self.settings.segmentation_dict["default"].my_dict)
        self.settings.set_in_profile("main_window_geometry", bytes(self.saveGeometry().toHex()).decode('ascii'))
        self.settings.dump(os.path.join(config_folder, "settings.json"))
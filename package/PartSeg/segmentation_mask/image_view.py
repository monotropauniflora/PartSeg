from qtpy.QtCore import QEvent, Qt, QRect
from qtpy.QtGui import QPainter, QPen, QColor
from qtpy.QtWidgets import QToolTip
from vispy.app import MouseEvent

from PartSeg.common_gui.channel_control import ChannelProperty
from ..common_gui.stack_image_view import ImageViewWithMask, ImageCanvas
from ..common_gui.napari_image_view import ImageView
import numpy as np


class StackImageView(ImageView):
    """
    :cvar settings: StackSettings
    """

    def __init__(self, settings, channel_property: ChannelProperty, name: str):
        super().__init__(settings, channel_property, name)
        self.viewer_widget.canvas.events.mouse_press.connect(self.component_click)
        # self.image_area.pixmap.click_signal.connect(self.component_click)

    def component_unmark(self, _num):
        pass

    def component_mark(self, num):
        pass

    def component_click(self, event: MouseEvent):
        cords = np.array([int(x) for x in self.viewer.active_layer.coordinates])
        for image_info in self.image_info.values():
            if not image_info.coords_in(cords):
                continue
            moved_coords = image_info.translated_coords(cords)
            component = image_info.segmentation_array[tuple(moved_coords)]
            if component:
                self.component_clicked.emit(component)

    def event(self, event: QEvent):
        if event.type() == QEvent.ToolTip and self.components:
            # text = str(self.component)
            text_list = []
            for el in self.components:
                if self.settings.component_is_chosen(el):
                    text_list.append("☑{}".format(el))
                else:
                    text_list.append("☐{}".format(el))
            QToolTip.showText(event.globalPos(), " ".join(text_list))
        return super().event(event)


class StackImageCanvas(ImageCanvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mark_component = None

    def set_mark(self, mark):
        self.mark_component = mark
        self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        if isinstance(self.mark_component, QRect):
            pen = QPen(QColor("white"))
            pen.setStyle(Qt.DashLine)
            pen.setDashPattern([5, 5])
            painter = QPainter(self)
            painter.setPen(pen)
            painter.drawRect(self.mark_component)


class StackImageViewOld(ImageViewWithMask):
    image_canvas = StackImageCanvas

    def __init__(self, settings, channel_property: ChannelProperty, name: str):
        super().__init__(settings, channel_property, name)
        self.image_area.pixmap.click_signal.connect(self.component_click)

    def component_unmark(self, _num):
        self.image_area.pixmap.set_mark(None)

    def component_mark(self, num):
        if self.labels_layer is not None:
            layers = self.labels_layer[self.stack_slider.value()]
            component = np.array(layers == num)
            if np.any(component):
                points = np.nonzero(component)
                scalar = self.image_area.pixmap.height() / component.shape[0]
                lower = np.min(points, 1) * scalar
                upper = np.max(points, 1) * scalar
                box_size = upper - lower
                rect = QRect(lower[1], lower[0], box_size[1], box_size[0])
                self.image_area.pixmap.set_mark(rect)
                return
        self.component_unmark(num)

    def component_click(self, point, size):
        if self.labels_layer is None:
            return
        x = int(point.x() / size.width() * self.image_shape.width())
        y = int(point.y() / size.height() * self.image_shape.height())
        num = self.labels_layer[self.stack_slider.value(), y, x]
        if num > 0:
            self.component_clicked.emit(num)

    def event(self, event: QEvent):
        if event.type() == QEvent.ToolTip and self.component is not None:
            # text = str(self.component)
            if self._settings.component_is_chosen(self.component):
                text = "☑{}".format(self.component)
            else:
                text = "☐{}".format(self.component)
            QToolTip.showText(event.globalPos(), text)
        return super().event(event)

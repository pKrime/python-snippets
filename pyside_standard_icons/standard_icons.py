"""
A list of the Qt standard icons
"""

from PySide import QtCore, QtGui


class StdIcoWin(QtGui.QWidget):
    """
    Contains a scrollable filtered list of icons
    """
    def __init__(self, *args, **kwargs):
        """

        :param parent: parent widget (default None)
        :type parent: QWidget
        :param f: WindowFlags (default 0)
        :type f: WindowFlags
        :param height: height of the widget (default 800)
        :type height: int
        """
        super(StdIcoWin, self).__init__(*args)
        self.setFixedHeight(kwargs.get("height", 800))
        self.setWhatsThis(__doc__)
        size_min = 3
        num_sizes = 4

        app = QtGui.QApplication.instance()
        ico_model = QtGui.QStandardItemModel(0, 1)
        ico_filter = QtGui.QSortFilterProxyModel()
        ico_filter.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        ico_filter.setSourceModel(ico_model)

        self.ico_list = QtGui.QListView()
        self.ico_list.setModel(ico_filter)

        # style options drop down box
        style_box = QtGui.QComboBox()
        for i, style in enumerate(QtGui.QStyleFactory.keys()):
            style_box.addItem(style)

            # set current style if matching, case insensitive
            if app.style().objectName().lower() == style.lower():
                style_box.setCurrentIndex(i)

        line_filter = QtGui.QLineEdit()
        line_filter.setPlaceholderText("Search Icon...")

        size_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        size_slider.setRange(size_min, size_min + num_sizes)
        size_slider.setSingleStep(1)
        size_slider.setPageStep(1)
        size_slider.setTickPosition(QtGui.QSlider.TicksAbove)

        self.size_label = QtGui.QLabel()

        scroll = QtGui.QScrollArea()
        scroll.setWidget(self.ico_list)
        scroll.setWidgetResizable(True)

        v_layout = QtGui.QVBoxLayout()
        f_layout = QtGui.QFormLayout()
        f_layout.addRow("window style", style_box)
        v_layout.addLayout(f_layout)
        v_layout.addWidget(self.size_label)
        v_layout.addWidget(size_slider)
        v_layout.addWidget(line_filter)
        v_layout.addWidget(scroll)

        # signals
        line_filter.textChanged.connect(ico_filter.setFilterFixedString)
        style_box.currentIndexChanged[str].connect(self.setAppStyle)
        size_slider.valueChanged.connect(self.setIconSize)

        # setting the slider also sets the size and size label
        size_slider.setSliderPosition(size_min + num_sizes / 2)
        self.setLayout(v_layout)
        self.populateIcons()

    def populateIcons(self):
        """
        Fill list of icons

        :return: None
        """
        model = self.ico_list.model().sourceModel()
        model.clear()
        self.ico_list.update()
        app = QtGui.QApplication.instance()

        # Get all StandardPixmap entries
        for style_itm in dir(QtGui.QStyle):
            if style_itm.startswith("SP_"):
                icon = app.style().standardIcon(getattr(QtGui.QStyle, style_itm))
                item = QtGui.QStandardItem(icon, style_itm)
                item.setEditable(False)
                model.appendRow((item,))

    def setAppStyle(self, style):
        """
        Set the app style and repopulate the list of icons

        :param style: style to use for the app
        :type style: QStyle
        :return: None
        """
        QtGui.QApplication.instance().setStyle(QtGui.QStyleFactory.create(style))
        self.populateIcons()

    def setIconSize(self, value):
        """
        Set the preferred size for the icons displayed in the list.
        The displayed size will be a power of two using the supplied value
        as exponent

        :param value: size level
        :type value: int
        :return: None
        """
        size = 2 ** value
        self.size_label.setText("icon size: {0}x{0}".format(size))
        self.ico_list.setIconSize(QtCore.QSize(size, size))


if __name__ == "__main__":
    import sys
    import os
    app = QtGui.QApplication(sys.argv)
    w = StdIcoWin()
    modname = os.path.splitext(os.path.basename(__file__))[0]
    w.setWindowTitle(modname.replace("_", " ").title())
    w.show()

    sys.exit(app.exec_())

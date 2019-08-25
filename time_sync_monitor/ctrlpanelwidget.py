from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph
from test_render_plot import *

class PrefBtn(QtWidgets.QPushButton):
    def __init__(self, name, is_enabled=True, parent=None):
        super(PrefBtn, self).__init__(parent)
        self.setMinimumHeight(30)
        self.setText(name)
        self.setEnabled(is_enabled)

class CtrlPanelWidget(object):

    def __init__(self, main_widget):

        #--- Create all buttons ---
        self.time_sync_stop_btn = PrefBtn("Stop")
        self.time_sync_start_btn = PrefBtn("Start")
        self.sync_line_stop_btn = PrefBtn("Stop")
        self.sync_line_start_btn = PrefBtn("Start")
        self.led_on_btn = PrefBtn("On")
        self.led_off_btn = PrefBtn("Off")
        self.led_all_on_btn = PrefBtn("All On")
        self.led_all_off_btn = PrefBtn("All Off")
        self.dfu_single_btn = PrefBtn("DFU Selected Node")
        self.dfu_all_btn = PrefBtn("DFU All")
        self.reset_btn = PrefBtn("Reset Selected Node")
        self.reset_all_btn = PrefBtn("Reset All")
        self.tx_pwr_btn = PrefBtn("Set Selected Node")
        self.tx_pwr_all_btn = PrefBtn("Set All")


        # --- Create all lists ---
        self.list_of_nodes = QtWidgets.QListWidget()
        self.list_of_nodes.setMinimumHeight(300)


        # --- Create all labels ---
        self.sync_line_label = QtWidgets.QLabel()
        self.sync_line_label.setText("Waiting for initialization")
        self.time_sync_label = QtWidgets.QLabel()
        self.time_sync_label.setText("Waiting for initialization")
        self.plot_sample_label = QtWidgets.QLabel()

        # --- Create all spaceritems ---
        self.spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)


        # --- Create all combo boxes ---
        self.tx_power_cbox = QtWidgets.QComboBox()
        self.tx_power_cbox.addItem('8 Dbm')
        self.tx_power_cbox.addItem('7 Dbm')
        self.tx_power_cbox.addItem('6 Dbm')
        self.tx_power_cbox.addItem('5 Dbm')
        self.tx_power_cbox.addItem('4 Dbm')
        self.tx_power_cbox.addItem('3 Dbm')
        self.tx_power_cbox.addItem('2 Dbm')
        self.tx_power_cbox.addItem('0 Dbm')
        self.tx_power_cbox.addItem('-4 Dbm')
        self.tx_power_cbox.addItem('-8 Dbm')
        self.tx_power_cbox.addItem('-12 Dbm')
        self.tx_power_cbox.addItem('-16 Dbm')
        self.tx_power_cbox.addItem('-20 Dbm')
        self.tx_power_cbox.addItem('-30 Dbm')
        self.tx_power_cbox.addItem('-40 Dbm')


        # --- Create all plots ---
        self.plot1 = TimeSyncPlot()
        self.plot1.addLegend()
        self.plot1.addLine(y=50)
        self.plot1.addLine(y=-50)
        self.plot2 = TimeSyncPlot(plot_partial=True)

        # --- Create all sliders ---
        self.horizontalSlider = QtWidgets.QSlider()
        self.horizontalSlider.setMaximum(200)
        self.horizontalSlider.setMinimum(5)
        self.horizontalSlider.setValue(50)
        self.horizontalSlider.setTickInterval(10)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)

        # ---  Create Available nodes group box ---
        self.nodes_gbox = QtWidgets.QGroupBox()
        self.nodes_gbox.setTitle("Available nodes")
        self.nodes_gbox_layout = QtWidgets.QVBoxLayout(self.nodes_gbox)
        self.nodes_gbox_layout.addWidget(self.list_of_nodes)


        #---  Create Syncronization line group box ---
        self.sync_line_gbox = QtWidgets.QGroupBox()
        self.sync_line_gbox.setTitle("Sync line")
        self.sync_line_gbox_layout = QtWidgets.QVBoxLayout(self.sync_line_gbox)
        self.sync_line_gbox_layout.addWidget(self.sync_line_label)
        self.sync_line_btn_layout = QtWidgets.QHBoxLayout()
        self.sync_line_btn_layout.addWidget(self.sync_line_start_btn)
        self.sync_line_btn_layout.addWidget(self.sync_line_stop_btn)
        self.sync_line_gbox_layout.addLayout(self.sync_line_btn_layout)


        # ---  Create Time syncronization group box ---
        self.time_sync_gbox = QtWidgets.QGroupBox()
        self.time_sync_gbox.setTitle("Time syncronization")
        self.time_sync_gbox_layout = QtWidgets.QVBoxLayout(self.time_sync_gbox)
        self.time_sync_btn_layout = QtWidgets.QHBoxLayout()
        self.time_sync_gbox_layout.addWidget(self.time_sync_label)
        self.time_sync_btn_layout.addWidget(self.time_sync_start_btn)
        self.time_sync_btn_layout.addWidget(self.time_sync_stop_btn)
        self.time_sync_gbox_layout.addLayout(self.time_sync_btn_layout)


        # ---  Create Led contoll group box ---
        self.led_gbox = QtWidgets.QGroupBox()
        self.led_gbox.setTitle("Led controller")
        self.led_gbox_layout = QtWidgets.QVBoxLayout(self.led_gbox)
        self.single_led_btn_layout = QtWidgets.QHBoxLayout()
        self.single_led_btn_layout.addWidget(self.led_on_btn)
        self.single_led_btn_layout.addWidget(self.led_off_btn)
        self.led_gbox_layout.addLayout(self.single_led_btn_layout)
        self.all_led_btn_layout = QtWidgets.QHBoxLayout()
        self.all_led_btn_layout.addWidget(self.led_all_on_btn)
        self.all_led_btn_layout.addWidget(self.led_all_off_btn)
        self.led_gbox_layout.addLayout(self.all_led_btn_layout)


        # ---  Create DFU group box ---
        self.dfu_gbox = QtWidgets.QGroupBox()
        self.dfu_gbox.setTitle("Device firmware update")
        self.dfu_gbox_layout = QtWidgets.QVBoxLayout(self.dfu_gbox)
        self.dfu_btn_layout = QtWidgets.QHBoxLayout()
        self.dfu_btn_layout.addWidget(self.dfu_single_btn)
        self.dfu_btn_layout.addWidget(self.dfu_all_btn)
        self.dfu_gbox_layout.addLayout(self.dfu_btn_layout)


        # ---  Create Reset group box ---
        self.reset_gbox = QtWidgets.QGroupBox()
        self.reset_gbox.setTitle("Reset")
        self.reset_gbox_layout = QtWidgets.QVBoxLayout(self.reset_gbox)
        self.reset_btn_layout = QtWidgets.QHBoxLayout()
        self.reset_btn_layout.addWidget(self.reset_btn)
        self.reset_btn_layout.addWidget(self.reset_all_btn)
        self.reset_gbox_layout.addLayout(self.reset_btn_layout)


        # ---  Create Tx Power group box ---
        self.tx_pwr_gbox = QtWidgets.QGroupBox()
        self.tx_pwr_gbox.setTitle("Node Tx Power")
        self.tx_pwr_gbox_layout = QtWidgets.QVBoxLayout(self.tx_pwr_gbox)
        self.tx_pwr_btn_layout = QtWidgets.QHBoxLayout()
        self.tx_pwr_btn_layout.addWidget(self.tx_pwr_btn)
        self.tx_pwr_btn_layout.addWidget(self.tx_pwr_all_btn)
        self.tx_pwr_gbox_layout.addWidget(self.tx_power_cbox)
        self.tx_pwr_gbox_layout.addLayout(self.tx_pwr_btn_layout)


        # --- Create Control Panel ---
        self.ctrl_widget = QtWidgets.QWidget()
        self.ctrl_widget.setMaximumSize(QtCore.QSize(308, 16777215))
        self.ctrl_layout = QtWidgets.QVBoxLayout(self.ctrl_widget)
        self.ctrl_layout.addWidget(self.nodes_gbox)
        self.ctrl_layout.addWidget(self.sync_line_gbox)
        self.ctrl_layout.addWidget(self.time_sync_gbox)
        self.ctrl_layout.addWidget(self.led_gbox)
        self.ctrl_layout.addWidget(self.dfu_gbox)
        self.ctrl_layout.addWidget(self.reset_gbox)
        self.ctrl_layout.addWidget(self.tx_pwr_gbox)


        # --- Create plot layout ---
        self.plot_layout = QtWidgets.QVBoxLayout()
        self.plot_layout.addWidget(self.plot1)
        self.plot_layout.addWidget(self.plot2)
        self.plot_layout.addWidget(self.plot_sample_label)
        self.slider_layout = QtWidgets.QHBoxLayout()
        self.slider_layout.addWidget(self.horizontalSlider)
        self.slider_layout.addItem(self.spacer)
        self.plot_layout.addLayout(self.slider_layout)

        # --- Create main layout ---
        main_widget.resize(1000, 700)
        main_widget.setWindowTitle("Command Panel")
        self.main_layout = QtWidgets.QHBoxLayout(main_widget)
        self.main_layout.addWidget(self.ctrl_widget)
        self.main_layout.addLayout(self.plot_layout)

        # Makes sure that the right widgets are not clickable at initialization point
        self.set_clickable_widgets(False)

    def set_clickable_widgets(self, on_off):
        self.sync_line_gbox.setEnabled(on_off)
        self.time_sync_gbox.setEnabled(on_off)
        self.led_on_btn.setEnabled(on_off)
        self.led_off_btn.setEnabled(on_off)
        self.dfu_single_btn.setEnabled(on_off)
        self.reset_btn.setEnabled(on_off)
        self.tx_pwr_btn.setEnabled(on_off)
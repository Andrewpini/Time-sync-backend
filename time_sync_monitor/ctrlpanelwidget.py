from PyQt5 import QtCore, QtGui, QtWidgets

class CtrlPanelWidget(object):

    def __init__(self, main_widget):

        #--- Create all buttons ---
        self.init_btn = QtWidgets.QPushButton()
        self.init_btn.setText("Initialize")
        self.time_sync_stop_btn = QtWidgets.QPushButton()
        self.time_sync_stop_btn.setText("Stop")
        self.time_sync_start_btn = QtWidgets.QPushButton()
        self.time_sync_start_btn.setText("Start")
        self.sync_line_stop_btn = QtWidgets.QPushButton()
        self.sync_line_stop_btn.setText("Stop")
        self.sync_line_start_btn = QtWidgets.QPushButton()
        self.sync_line_start_btn.setText("Start")
        self.led_on_btn = QtWidgets.QPushButton()
        self.led_on_btn.setText("On")
        self.led_off_btn = QtWidgets.QPushButton()
        self.led_off_btn.setText("Off")
        self.led_all_on_btn = QtWidgets.QPushButton()
        self.led_all_on_btn.setText("All On")
        self.led_all_off_btn = QtWidgets.QPushButton()
        self.led_all_off_btn.setText("All Off")
        self.dfu_single_btn = QtWidgets.QPushButton()
        self.dfu_single_btn.setText("DFU Selected Node")
        self.dfu_all_btn = QtWidgets.QPushButton()
        self.dfu_all_btn.setText("DFU All")
        self.reset_btn = QtWidgets.QPushButton()
        self.reset_btn.setText("Reset Selected Node")
        self.reset_all_btn = QtWidgets.QPushButton()
        self.reset_all_btn.setText("Reset All")

        # --- Create all lists ---
        self.list_of_nodes = QtWidgets.QListWidget()


        # --- Create all labels ---
        self.sync_line_label = QtWidgets.QLabel()
        self.sync_line_label.setText("Waiting for initialization")
        self.time_sync_label = QtWidgets.QLabel()
        self.time_sync_label.setText("Waiting for initialization")


        # --- Create all combo boxes ---
        self.sync_line_selector = QtWidgets.QComboBox()
        self.time_sync_selector = QtWidgets.QComboBox()


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


        # ---  Create Available nodes group box ---
        self.nodes_gbox = QtWidgets.QGroupBox()
        self.nodes_gbox.setTitle("Available nodes")
        self.nodes_gbox_layout = QtWidgets.QVBoxLayout(self.nodes_gbox)
        self.nodes_gbox_layout.addWidget(self.list_of_nodes)


        #--- Create main layout ---
        main_widget.resize(332, 549)
        main_widget.setWindowTitle("Command Panel")
        self.main_layout = QtWidgets.QVBoxLayout(main_widget)
        self.main_layout.addWidget(self.nodes_gbox)
        self.main_layout.addWidget(self.sync_line_gbox)
        self.main_layout.addWidget(self.time_sync_gbox)
        self.main_layout.addWidget(self.led_gbox)
        self.main_layout.addWidget(self.dfu_gbox)
        self.main_layout.addWidget(self.reset_gbox)
        self.set_clickable_widgets(False)

    def set_clickable_widgets(self, on_off):
        self.sync_line_gbox.setEnabled(on_off)
        self.time_sync_gbox.setEnabled(on_off)
        self.led_on_btn.setEnabled(on_off)
        self.led_off_btn.setEnabled(on_off)
        self.dfu_single_btn.setEnabled(on_off)
        self.reset_btn.setEnabled(on_off)
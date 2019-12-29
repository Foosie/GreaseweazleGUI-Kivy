# gui.py
#
# Greaseweazle GUI Wrapper
#
# Copyright (c) 2019 Don Mankin <don.mankin@yahoo.com>
#
# MIT License
#
# See the file LICENSE more details, or visit <https://opensource.org/licenses/MIT>.


from kivy.config import Config
#Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '680')
Config.set('graphics', 'height', '560')

from kivy.lang import Builder
from kivy.app import App
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
import serial.tools.list_ports
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock
from kivy.core.window import Window

import sys
import psutil
import ntpath
import subprocess
import os
if os.name == 'nt':
    from subprocess import Popen, CREATE_NEW_CONSOLE
else:
    from subprocess import Popen

class MainScreen(Screen):

    # read from disk
    txtCommandLineRFD = ObjectProperty(TextInput())
    chkRevsPerTrack = ObjectProperty(CheckBox())
    txtRevsPerTrack = ObjectProperty(TextInput())
    chkFirstCylToRead = ObjectProperty(CheckBox())
    txtFirstCylToRead = ObjectProperty(TextInput())
    chkLastCylToRead = ObjectProperty(CheckBox())
    txtLastCylToRead = ObjectProperty(TextInput())
    tglSingleSidedRFD = ObjectProperty(ToggleButton())
    tglDoubleSidedRFD = ObjectProperty(ToggleButton())

    # write to disk
    txtCommandLineWTD = ObjectProperty(TextInput())
    chkAdjustSpeed = ObjectProperty(CheckBox())
    chkFirstCylToWrite = ObjectProperty(CheckBox())
    txtFirstCylToWrite = ObjectProperty(TextInput())
    chkLastCylToWrite = ObjectProperty(CheckBox())
    txtLastCylToWrite = ObjectProperty(TextInput())
    tglSingleSidedWTD = ObjectProperty(ToggleButton())
    tglDoubleSidedWTD = ObjectProperty(ToggleButton())

    # set delays
    txtCommandLineDelays = ObjectProperty(TextInput())
    chkDelayAfterSelect = ObjectProperty(CheckBox())
    txtDelayAfterSelect = ObjectProperty(TextInput())
    chkDelayBetweenSteps = ObjectProperty(CheckBox())
    txtDelayBetweenSteps = ObjectProperty(TextInput())
    chkSettleDelayAfterSeek = ObjectProperty(CheckBox())
    txtSettleDelayAfterSeek = ObjectProperty(TextInput())
    chkDelayUntilAutoDeselect = ObjectProperty(CheckBox())
    txtDelayUntilAutoDeselect = ObjectProperty(TextInput())

    # update firmware
    txtCommandLineFirmware = ObjectProperty(TextInput())

    # global variables
    gw_commports = ObjectProperty(None)
    gw_comm_port = ObjectProperty(None)
    gw_file_name = ObjectProperty(None)
    gw_folder_name = ObjectProperty(None)
    gw_application_folder = ObjectProperty(None)
    gw_dirty = BooleanProperty(None)
    gw_window_pid = ObjectProperty(None)

    # initialize variables
    gw_commports = serial.tools.list_ports.comports()
    gw_comm_port = "COM1"
    gw_file_name = "mydisk.scp"
    gw_folder_name = ""
    gw_dirty = False
    gw_window_pid = -1

    if os.name == 'nt':
        gw_application_folder = sys.path[0] + "\\"
    else:
        gw_application_folder = sys.path[0] + "/"

    # override function so we can process focus behavior
    class FocusTabbedPanelItem(FocusBehavior, TabbedPanelItem):
        def on_parent(self, widget, parent):
            self.focus = True

    def change_command_lines_port(self, btn):
        self.gw_comm_port = btn.text
        cmdline = self.ids.txtCommandLineRFD.text
        idx = self.find_str(cmdline, "COM")
        if idx != -1:
            left_str = cmdline[0:idx]
            cmdline = left_str + self.gw_comm_port
            self.ids.txtCommandLineRFD.text = cmdline

        cmdline = self.ids.txtCommandLineWTD.text
        idx = self.find_str(cmdline, "COM")
        if idx != -1:
            left_str = cmdline[0:idx]
            cmdline = left_str + self.gw_comm_port
            self.ids.txtCommandLineWTD.text = cmdline

        cmdline = self.ids.txtCommandLineDelays.text
        idx = self.find_str(cmdline, "COM")
        if idx != -1:
            left_str = cmdline[0:idx]
            cmdline = left_str + self.gw_comm_port
            self.ids.txtCommandLineDelays.text = cmdline

        cmdline = self.ids.txtCommandLineFirmware.text
        idx = self.find_str(cmdline, "COM")
        if idx != -1:
            left_str = cmdline[0:idx]
            cmdline = left_str + self.gw_comm_port
            self.ids.txtCommandLineFirmware.text = cmdline

        # indicate we need a refresh
        self.gw_dirty = True

    def build_read_from_disk(self):
        file_spec = os.path.join(self.gw_folder_name, self.gw_file_name)
        if os.name == "nt":
            cmdline = "\"python \"" + self.gw_application_folder + "gw.py\" read "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + "gw.py\' read "
        if self.ids.chkRevsPerTrack.active:
            cmdline += "--revs=" + self.ids.txtRevsPerTrack.text + " "
        if self.ids.chkFirstCylToRead.active:
            cmdline += "--scyl=" + self.ids.txtFirstCylToRead.text + " "
        if self.ids.chkLastCylToRead.active:
            cmdline += "--ecyl=" + self.ids.txtLastCylToRead.text + " "
        if self.ids.tglSingleSidedRFD.state == "down":
            cmdline += "--single-sided "
        if os.name == "nt":
            cmdline += "'" + file_spec + "' " + self.gw_comm_port + "\""
        else:
            cmdline += "'" + file_spec + "' " + self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineRFD.text = cmdline

    def build_write_to_disk(self):
        file_spec = os.path.join(self.gw_folder_name, self.gw_file_name)
        if os.name == "nt":
            cmdline = "\"python \"" + self.gw_application_folder + "gw.py\" write "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + "gw.py\' write "
        if self.ids.chkAdjustSpeed.active:
            cmdline += "--adjust-speed "
        if self.ids.chkFirstCylToWrite.active:
            cmdline += "--scyl=" + self.ids.txtFirstCylToWrite.text + " "
        if self.ids.chkLastCylToWrite.active:
            cmdline += "--ecyl=" + self.ids.txtLastCylToWrite.text + " "
        if self.ids.tglSingleSidedWTD.state == "down":
            cmdline += "--single-sided "
        if os.name == "nt":
            cmdline += "'" + file_spec + "' " + self.gw_comm_port + "\""
        else:
            cmdline += "'" + file_spec + "' " + self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineWTD.text = cmdline

    def build_set_delays(self):
        if os.name == "nt":
            cmdline = "python \"" + self.gw_application_folder + "gw.py\" delays "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + "gw.py\' delays "
        if self.ids.chkDelayAfterSelect.active:
            cmdline += "--select=" + self.ids.txtDelayAfterSelect.text + " "
        if self.ids.chkDelayBetweenSteps.active:
            cmdline += "--step=" + self.ids.txtDelayBetweenSteps.text + " "
        if self.ids.chkSettleDelayAfterSeek.active:
            cmdline += "--settle=" + self.ids.txtSettleDelayAfterSeek.text + " "
        if self.ids.chkDelayAfterMotorOn.active:
            cmdline += "--motor=" + self.ids.txtDelayAfterMotorOn.text + " "
        if self.ids.chkDelayUntilAutoDeselect.active:
            cmdline += "--auto-off=" + self.ids.txtDelayUntilAutoDeselect.text + " "
        if os.name == "nt":
            cmdline += self.gw_comm_port + "\""
        else:
            cmdline += self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineDelays.text = cmdline

    def build_update_firmware(self):
        file_spec = os.path.join(self.gw_folder_name, self.gw_file_name)
        if os.name == "nt":
            cmdline = "python \"" + self.gw_application_folder + "gw.py\" update "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + "gw.py\' update "
        if os.name == "nt":
            cmdline += "'" + file_spec + "' " + self.gw_comm_port + "\""
        else:
            cmdline += "'" + file_spec + "' " + self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineFirmware.text = cmdline

    def process_read_from_disk(self):
        if os.name == 'nt':
            if not self.checkIfProcessRunning(self.gw_window_pid):
                command_line = "C:\\Windows\System32\\cmd.exe /K " + self.ids.txtCommandLineRFD.text
                p = subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
                self.gw_window_pid = p.pid
            else:
                self.parent.parent.ids['screen_manager'].current = 'error_screen'
        else:
            #if not self.checkIfProcessRunningByName("gw.py"):
            if True:
                command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineRFD.text
                p = subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                self.gw_window_pid = p.pid
            else:
                self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_write_to_disk(self):
        if os.name == 'nt':
            if not self.checkIfProcessRunning(self.gw_window_pid):
                command_line = "C:\\Windows\System32\\cmd.exe /K " + self.ids.txtCommandLineWTD.text
                p = subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
                self.gw_window_pid = p.pid
            else:
                self.parent.parent.ids['screen_manager'].current = 'error_screen'
        else:
            #if not self.checkIfProcessRunningByName("gw.py"):
            if True:
                command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineWTD.text
                p = subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                self.gw_window_pid = p.pid
            else:
                self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_set_delays(self):
        if os.name == 'nt':
            if not self.checkIfProcessRunning(self.gw_window_pid):
                command_line = "C:\\Windows\System32\\cmd.exe /K " + self.ids.txtCommandLineDelays.text
                p = subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
                self.gw_window_pid = p.pid
            else:
                self.parent.parent.ids['screen_manager'].current = 'error_screen'
        else:
            if True:
            #if not self.checkIfProcessRunningByName("gw.py"):
                command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineDelays.text
                p = subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                self.gw_window_pid = p.pid
            else:
                self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_update_firmware(self):
        if os.name == 'nt':
            if not self.checkIfProcessRunning(self.gw_window_pid):
                command_line = "C:\\Windows\System32\\cmd.exe /K " + self.ids.txtCommandLineFirmware.text
                p = subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
                self.gw_window_pid = p.pid
            else:
                self.parent.parent.ids['screen_manager'].current = 'error_screen'
        else:
            if True:
            #if not self.checkIfProcessRunningByName("gw.py"):
                command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineFirmware.text
                p = subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                self.gw_window_pid = p.pid
            else:
                self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_select_file_firmware(self):
        self.self.gw_dirty = True  # indicate we need a refresh

    def got_focus_write_to_disk(self):
        self.build_write_to_disk()

    def got_focus_read_from_disk(self):
        self.build_read_from_disk()

    def got_focus_set_delays(self):
        self.build_set_delays()

    def got_focus_update_firmware(self):
        self.build_update_firmware()

    def got_focus_configuration(self, box_layout):
        self.create_comm_buttons(box_layout)

    def create_comm_buttons(self, box_layout):
        box_layout.clear_widgets()
        for comport in serial.tools.list_ports.comports():
            btn = ToggleButton(markup=True)
            btn.text = comport.device
            btn.group = "comm"
            btn.bind(on_release=lambda x=btn:self.change_command_lines_port(x))
            box_layout.add_widget(btn)

    def find_str(self, s, char):
        index = 0
        if char in s:
            c = char[0]
            for ch in s:
                if ch == c:
                    if s[index:index + len(char)] == char:
                        return index
                index += 1
        return -1

    def dirty_check(self, dt):
        if self.main_screen.gw_dirty:
            self.main_screen.build_read_from_disk(self)
            self.main_screen.build_write_to_disk(self)
            self.main_screen.build_set_delays(self)
            self.main_screen.build_update_firmware(self)
            self.main_screen.gw_dirty = False

    def checkIfProcessRunning(self, pid):
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if pid == proc.pid:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def checkIfProcessRunningByName(self, name):  # broken
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                for l in proc.cmdline():
                    if "gui.py" in l.lower():
                        print("cmdline = " + l)
                # Check if process name contains the given name string.
                if name.lower() == proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.main_screen = MainScreen
        self.file_dialog_screen = FileDialogScreen
        self.folder_dialog_screen = FolderDialogScreen
        self.main_screen.gw_dirty = True  # initialize
        Clock.schedule_interval(self.dirty_check, 0.5)

class FileDialogScreen(Screen):

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.main_screen = MainScreen

    def set_file_name(self, fn):
        head, tail = ntpath.split(fn)
        self.main_screen.gw_folder_name = head
        self.main_screen.gw_file_name = tail
        self.main_screen.gw_file_spec = fn
        self.main_screen.gw_dirty = True

class FileUpdateDialogScreen(Screen):

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.main_screen = MainScreen

    def set_file_name(self, fn):
        head, tail = ntpath.split(fn)
        self.main_screen.gw_folder_name = head
        self.main_screen.gw_file_name = tail
        self.main_screen.gw_file_spec = fn
        self.main_screen.gw_dirty = True

class FolderDialogScreen(Screen):

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.main_screen = MainScreen

    def set_folder_name(self, fn):
        self.main_screen.gw_folder_name = fn
        self.main_screen.gw_dirty = True

class ErrorScreen(Screen):
    pass

GUI = Builder.load_file("gui.kv")
class MainApp(App):
    title = "GreaseweazleGUI v0.28 / Host Tools v0.7 - by Don Mankin"
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        return GUI
    def change_screen(self, screen_name):
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name
    def on_request_close(self, *args):
        main_screen = self.root.ids['main_screen']
        screen_manager = self.root.ids['screen_manager']
        if os.name == "nt":
            if main_screen.checkIfProcessRunning(main_screen.gw_window_pid):
                screen_manager.current = 'error_screen'
                return True
            else:
                return False
        else:  # not working in linux
            return False

MainApp().run()

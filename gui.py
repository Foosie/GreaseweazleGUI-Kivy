# gui.py
#
# Greaseweazle GUI Wrapper
#
# Copyright (c) 2019 Don Mankin <don.mankin@yahoo.com>
#
# MIT License
#
# See the file LICENSE for more details, or visit <https://opensource.org/licenses/MIT>.


from kivy.config import Config

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
import os.path
import configparser

if sys.platform == 'win32':
    from subprocess import Popen, CREATE_NEW_CONSOLE
else:
    from subprocess import Popen

Config.set('graphics', 'width', '680')
Config.set('graphics', 'height', '560')

class MainScreen(Screen):

    # read from disk
    txtCommandLineRFD = ObjectProperty(TextInput())
    chkRevsPerTrack = ObjectProperty(CheckBox())
    txtRevsPerTrack = ObjectProperty(TextInput())
    chkFirstCylToRead = ObjectProperty(CheckBox())
    txtFirstCylToRead = ObjectProperty(TextInput())
    chkLastCylToRead = ObjectProperty(CheckBox())
    txtLastCylToRead = ObjectProperty(TextInput())
    chkSelectDriveRFD = ObjectProperty(CheckBox())
    txtSelectDriveRFD = ObjectProperty(TextInput())
    chkRateRFD = ObjectProperty(CheckBox())
    txtRateRFD = ObjectProperty(TextInput())
    chkRpmRFD = ObjectProperty(CheckBox())
    txtRpmRFD = ObjectProperty(TextInput())
    tglUseExeRFD = ObjectProperty(ToggleButton())
    tglSingleSidedRFD = ObjectProperty(ToggleButton())
    tglSingleSidedLegacyRFD = ObjectProperty(ToggleButton())
    chkDoubleStepRFD = ObjectProperty(CheckBox())

    # write to disk
    txtCommandLineWTD = ObjectProperty(TextInput())
    chkAdjustSpeed = ObjectProperty(CheckBox())
    chkDoubleStepWTD = ObjectProperty(CheckBox())
    chkEraseEmptyWTD = ObjectProperty(CheckBox())
    chkFirstCylToWrite = ObjectProperty(CheckBox())
    txtFirstCylToWrite = ObjectProperty(TextInput())
    chkLastCylToWrite = ObjectProperty(CheckBox())
    txtLastCylToWrite = ObjectProperty(TextInput())
    chkSelectDriveWTD = ObjectProperty(CheckBox())
    txtSelectDriveWTD = ObjectProperty(TextInput())
    tglUseExeWTD = ObjectProperty(ToggleButton())
    tglSingleSidedWTD = ObjectProperty(ToggleButton())

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
    tglUseExeDelays = ObjectProperty(ToggleButton())

    # update firmware
    txtCommandLineFirmware = ObjectProperty(TextInput())
    tglUseExeFW = ObjectProperty(ToggleButton())
    tglBootloader = ObjectProperty(ToggleButton())

    # pin level
    txtPinLevel = ObjectProperty(TextInput())
    chkHighLevel = ObjectProperty(CheckBox())
    chkLowLevel = ObjectProperty(CheckBox())
    txtCommandLinePinLevel = ObjectProperty(TextInput())
    tglUseExePinLevel = ObjectProperty(ToggleButton())

    # seek cylinder
    txtSeekCyl = ObjectProperty(TextInput())
    txtCommandLineSeekCyl = ObjectProperty(TextInput())
    chkSelectDriveSeelCyl = ObjectProperty(CheckBox())
    tglUseExeSeekCyl = ObjectProperty(ToggleButton())

    # reset
    txtCommandLineReset = ObjectProperty(TextInput())
    tglUseExeReset = ObjectProperty(ToggleButton())

    # bandwidth
    txtCommandLineBandwidth = ObjectProperty(TextInput())
    tglUseExeBandwidth = ObjectProperty(ToggleButton())

    # info
    txtCommandLineInfo = ObjectProperty(TextInput())
    tglUseExeInfo = ObjectProperty(ToggleButton())
    tglInfoBootloader = ObjectProperty(ToggleButton())

    # global variables
    gw_application_folder = ObjectProperty(None)
    gw_dirty = BooleanProperty(None)
    gw_window_pid = ObjectProperty(None)

    # initialize variables
    gw_commports = serial.tools.list_ports.comports()

    # later versions of greaseweazle don't require a port designator
    gw_comm_port = ""

    gw_iniFilespec = "./gui.ini"
    gw_bUseExe = False;
    gw_RFDFilename = "mydisk.scp"
    gw_RFDFolder = "./"
    gw_WTDFilename = "mydisk.scp"
    gw_WTDFolder = "./"
    gw_UpdateFWFilename = "Greaseweazle-v0.6.upd"
    gw_UpdateFWFolder = "./"
    gw_folder_name = ""
    gw_dirty = False
    gw_window_pid = -1

    # get application folder
    if sys.platform == 'win32':
        gw_application_folder = sys.path[0] + "\\"
    else:
        gw_application_folder = sys.path[0] + "/"

    # set script name
    if sys.platform == 'win32':
        gw_script = sys.path[0] + "\\" + "gw"
    else:
        gw_script = sys.path[0] + "/" + "gw"
    if os.path.isfile(gw_script):
        gw_script = "gw"
    else:
        gw_script = "gw.py"

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
        if self.ids.tglUseExeRFD.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")
        file_spec = os.path.join(self.main_screen.gw_RFDFolder, self.main_screen.gw_RFDFilename)
        if sys.platform == 'win32':
            if self.ids.tglUseExeRFD.state == "down":
                cmdline = "\"gw.exe read "
            else:
                cmdline = "\"python \"" + self.gw_application_folder + self.gw_script + "\" read "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' read "
        if self.ids.chkDoubleStepRFD.active:
            cmdline += "--double-step "
        if self.ids.chkRevsPerTrack.active:
            cmdline += "--revs=" + self.ids.txtRevsPerTrack.text + " "
        if self.ids.chkFirstCylToRead.active:
            cmdline += "--scyl=" + self.ids.txtFirstCylToRead.text + " "
        if self.ids.chkLastCylToRead.active:
            cmdline += "--ecyl=" + self.ids.txtLastCylToRead.text + " "
        if self.ids.chkSelectDriveRFD.active:
            cmdline += "--drive=" + self.ids.txtSelectDriveRFD.text + " "
        if self.ids.chkRateRFD.active:
            cmdline += "--rate=" + self.ids.txtRateRFD.text + " "
        if self.ids.chkRpmRFD.active:
            cmdline += "--rpm=" + self.ids.txtRpmRFD.text + " "
        if self.ids.tglSingleSidedRFD.state == "down":
            cmdline += "--single-sided "
        cmdline += "'" + file_spec;
        if self.ids.tglSingleSidedRFD.state == "down" and self.ids.tglSingleSidedLegacyRFD.state == "down":
            cmdline += "::legacy_ss"
        cmdline += "' " + self.gw_comm_port;
        if (sys.platform == 'win32') or (sys.platform == 'darwin'):
            cmdline += "\""
        else:
            cmdline +=  ";read -n1\""
        self.ids.txtCommandLineRFD.text = cmdline

    def build_write_to_disk(self):
        if self.ids.tglUseExeWTD.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")

        file_spec = os.path.join(self.main_screen.gw_WTDFolder, self.main_screen.gw_WTDFilename)
        if sys.platform == 'win32':
            if self.ids.tglUseExeWTD.state == "down":
                cmdline = "\"gw.exe write "
            else:
                cmdline = "\"python \"" + self.gw_application_folder + self.gw_script + "\" write "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' write "
        if self.ids.chkAdjustSpeed.active:
            cmdline += "--adjust-speed "
        if self.ids.chkDoubleStepWTD.active:
            cmdline += "--double-step "
        if self.ids.chkEraseEmptyWTD.active:
            cmdline += "--erase-empty "
        if self.ids.chkFirstCylToWrite.active:
            cmdline += "--scyl=" + self.ids.txtFirstCylToWrite.text + " "
        if self.ids.chkLastCylToWrite.active:
            cmdline += "--ecyl=" + self.ids.txtLastCylToWrite.text + " "
        if self.ids.tglSingleSidedWTD.state == "down":
            cmdline += "--single-sided "
        if self.ids.chkSelectDriveWTD.active:
            cmdline += "--drive=" + self.ids.txtSelectDriveWTD.text + " "
        if (sys.platform == 'win32') or (sys.platform == 'darwin'):
            cmdline += "'" + file_spec + "' " + self.gw_comm_port + "\""
        else:
            cmdline += "'" + file_spec + "' " + self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineWTD.text = cmdline

    def build_erase_disk(self):
        if self.ids.tglUseExeErase.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")

        if sys.platform == 'win32':
            if self.ids.tglUseExeErase.state == "down":
                cmdline = "\"gw.exe erase "
            else:
                cmdline = "\"python \"" + self.gw_application_folder + self.gw_script + "\" erase "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' erase "
        if self.ids.chkFirstCylToErase.active:
            cmdline += "--scyl=" + self.ids.txtFirstCylToErase.text + " "
        if self.ids.chkLastCylToErase.active:
            cmdline += "--ecyl=" + self.ids.txtLastCylToErase.text + " "
        if self.ids.tglSingleSidedErase.state == "down":
            cmdline += "--single-sided "
        if self.ids.chkSelectDriveErase.active:
            cmdline += "--drive=" + self.ids.txtSelectDriveErase.text + " "
        if (sys.platform == 'win32') or (sys.platform == 'darwin'):
            cmdline += self.gw_comm_port + "\""
        else:
            cmdline += self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineErase.text = cmdline

    def build_set_delays(self):
        if self.ids.tglUseExeDelays.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")

        if sys.platform == 'win32':
            if self.ids.tglUseExeDelays.state == "down":
                cmdline = "\"gw.exe delays "
            else:
                cmdline = "python \"" + self.gw_application_folder + self.gw_script + "\" delays "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' delays "
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
        if (sys.platform == 'win32') or (sys.platform == 'darwin'):
            cmdline += self.gw_comm_port + "\""
        else:
            cmdline += self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineDelays.text = cmdline

    def build_seek_cyl(self):
        if self.ids.tglUseExeSeekCyl.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")

        if sys.platform == 'win32':
            if self.ids.tglUseExeDelays.state == "down":
                cmdline = "gw.exe seek "
            else:
                cmdline = "python \"" + self.gw_application_folder + self.gw_script + "\" seek "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' seek "

        if self.ids.chkSelectDriveSeekCyl.active:
            cmdline += "--drive=" + self.ids.txtSelectDriveSeekCyl.text + " "

        self.ids.txtCommandLineSeekCyl.text = cmdline + self.ids.txtSeekCyl.text

    def build_update_firmware(self):
        if self.ids.tglUseExeFW.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")

        file_spec = os.path.join(self.main_screen.gw_UpdateFWFolder, self.main_screen.gw_UpdateFWFilename)
        if sys.platform == 'win32':
            if self.ids.tglUseExeFW.state == "down":
                cmdline = "\"gw.exe update "
            else:
                cmdline = "python \"" + self.gw_application_folder + self.gw_script + "\" update "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' update "
        if self.ids.tglBootloader.state == "down":
            cmdline += "--bootloader "
        if sys.platform == 'win32':
            cmdline += "'" + file_spec + "' " + self.gw_comm_port + "\""
        else:
            if sys.platform == 'darwin':
                cmdline += "'" + file_spec + "' " + self.gw_comm_port + "\""
            else:
                cmdline += "'" + file_spec + "' " + self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineFirmware.text = cmdline

    def build_pin_level(self):
        if self.ids.tglUseExePinLevel.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")

        if sys.platform == 'win32':
            if self.ids.tglUseExePinLevel.state == "down":
                cmdline = "\"gw.exe pin "
            else:
                cmdline = "python \"" + self.gw_application_folder + self.gw_script + "\" pin "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' pin "
        cmdline += self.ids.txtPinLevel.text
        if self.ids.chkHighLevel.active == 'True':
            cmdline += " H"
        else:
            cmdline += " L"
        if (len(self.gw_comm_port) > 0):
            if sys.platform == 'win32' or sys.platform == 'darwin':
                cmdline += " " + self.gw_comm_port + "\""
            else:
                cmdline += " " + self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLinePinLevel.text = cmdline

    def build_reset(self):
        if self.ids.tglUseExeReset.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")

        if sys.platform == 'win32':
            if self.ids.tglUseExeReset.state == "down":
                cmdline = "\"gw.exe reset "
            else:
                cmdline = "python \"" + self.gw_application_folder + self.gw_script + "\" reset "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' reset "
        if sys.platform == 'win32' or sys.platform == 'darwin':
            cmdline += self.gw_comm_port + "\""
        else:
            cmdline += self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineReset.text = cmdline

    def build_bandwidth(self):
        if self.ids.tglUseExeBandwidth.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")

        if sys.platform == 'win32':
            if self.ids.tglUseExeBandwidth.state == "down":
                cmdline = "\"gw.exe bandwidth "
            else:
                cmdline = "python \"" + self.gw_application_folder + self.gw_script + "\" bandwidth "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' bandwidth "
        if sys.platform == 'win32' or sys.platform == 'darwin':
            cmdline += self.gw_comm_port + "\""
        else:
            cmdline += self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineBandwidth.text = cmdline

    def build_info(self):
        if self.ids.tglUseExeInfo.state == "down":
            self.set_exe_mode("True")
        else:
            self.set_exe_mode("False")
        if sys.platform == 'win32':
            if self.ids.tglUseExeInfo.state == "down":
                cmdline = "\"gw.exe info "
            else:
                cmdline = "python \"" + self.gw_application_folder + self.gw_script + "\" info "
        else:
            cmdline = "\"" + "python " + " \'" + self.gw_application_folder + self.gw_script + "\' info "
        if self.ids.tglInfoBootloader.state == "down":
            cmdline += "--bootloader "
        if sys.platform == 'win32' or sys.platform == 'darwin':
            cmdline += self.gw_comm_port + "\""
        else:
            cmdline += self.gw_comm_port + ";read -n1\""
        self.ids.txtCommandLineInfo.text = cmdline

    def process_read_from_disk(self):
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLineRFD.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    #command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLineRFD.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLineRFD.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineRFD.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_write_to_disk(self):
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLineWTD.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    #command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLineWTD.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLineWTD.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineWTD.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_erase_disk(self):
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLineErase.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    #command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLineErase.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLineErase.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineErase.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_set_delays(self):
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLineDelays.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    #command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLineDelays.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLineDelays.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineDelays.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_seek_cyl(self):
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLineSeekCyl.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    # command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLineSeekCyl.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLineSeekCyl.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineSeekCyl.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_update_firmware(self):
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLineFirmware.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    #command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLineFirmware.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLineFirmware.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineFirmware.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_pin_level(self):
        self.build_pin_level()
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLinePinLevel.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    #command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLinePinLevel.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLinePinLevel.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLinePinLevel.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_reset(self):
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLineReset.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    #command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLineReset.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLineReset.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineReset.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_bandwidth(self):
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLineBandwidth.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    #command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLineBandwidth.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLineBandwidth.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineBandwidth.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def process_info(self):
        if not self.checkIfProcessRunningByScript("gw.py") and not self.checkIfProcessRunningByScript("gw.exe"):
            self.iniWriteFile()
            if sys.platform == 'win32':
                command_line = "C:\Windows\System32\cmd.exe /K " + self.ids.txtCommandLineInfo.text
                subprocess.Popen(command_line, creationflags=CREATE_NEW_CONSOLE, env=os.environ.copy())
            else:
                if sys.platform == 'darwin':
                    #command_line = "osascript -e 'tell application \"Terminal\" to do script \"" + self.ids.txtCommandLineInfo.text + "\"'"
                    command_line = "osascript -e 'tell application \"Terminal\" to do script " + self.ids.txtCommandLineInfo.text + "'"
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
                else:
                    command_line = "gnome-terminal -x bash -c " + self.ids.txtCommandLineInfo.text
                    subprocess.Popen(command_line, shell=True, env=os.environ.copy())
        else:
            self.parent.parent.ids['screen_manager'].current = 'error_screen'

    def got_focus_write_to_disk(self):
        self.build_write_to_disk()

    def got_focus_erase_disk(self):
        self.build_erase_disk()

    def got_focus_read_from_disk(self):
        self.build_read_from_disk()

    def got_focus_set_delays(self):
        self.build_set_delays()

    def got_focus_seek_cyl(self):
        self.build_seek_cyl()

    def got_focus_update_firmware(self):
        self.build_update_firmware()

    def got_focus_pin_level(self):
        self.build_pin_level()

    def got_focus_reset(self):
        self.build_reset()

    def got_focus_bandwidth(self):
        self.build_bandwidth()

    def got_focus_info(self):
        self.build_info()

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

    def clear_port(self):
        self.gw_comm_port = ""

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
            self.main_screen.build_erase_disk(self)
            self.main_screen.build_set_delays(self)
            self.main_screen.build_update_firmware(self)
            self.main_screen.build_pin_level(self)
            self.main_screen.build_reset(self)
            self.main_screen.build_bandwidth(self)
            self.main_screen.build_info(self)
            self.main_screen.gw_dirty = False

    def checkIfProcessRunningByScript(self, script):
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                for l in proc.cmdline():
                    if script in l.lower():
                        #print("cmdline = " + l)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def set_exe_mode(self, state):
        if state == "True":
            self.ids.tglUseExeRFD.active = True
            self.ids.tglUseExeRFD.state = 'down'
            self.ids.tglUseExeWTD.active = True
            self.ids.tglUseExeWTD.state = 'down'
            self.ids.tglUseExeWTD.active = True
            self.ids.tglUseExeWTD.state = 'down'
            self.ids.tglUseExeErase.active = True
            self.ids.tglUseExeErase.state = 'down'
            self.ids.tglUseExeDelays.active = True
            self.ids.tglUseExeDelays.state = 'down'
            self.ids.tglUseExeFW.active = True
            self.ids.tglUseExeFW.state = 'down'
            self.ids.tglUseExePinLevel.active = True
            self.ids.tglUseExePinLevel.state = 'down'
            self.ids.tglUseExeReset.active = True
            self.ids.tglUseExeReset.state = 'down'
            self.ids.tglUseExeBandwidth.active = True
            self.ids.tglUseExeBandwidth.state = 'down'
            self.ids.tglUseExeInfo.active = True
            self.ids.tglUseExeInfo.state = 'down'
            self.ids.tglUseExeSeekCyl.active = True
            self.ids.tglUseExeSeekCyl.state = 'down'
        else:
            self.ids.tglUseExeRFD.active = False
            self.ids.tglUseExeRFD.state = 'normal'
            self.ids.tglUseExeWTD.active = False
            self.ids.tglUseExeWTD.state = 'normal'
            self.ids.tglUseExeWTD.active = False
            self.ids.tglUseExeWTD.state = 'normal'
            self.ids.tglUseExeErase.active = False
            self.ids.tglUseExeErase.state = 'normal'
            self.ids.tglUseExeDelays.active = False
            self.ids.tglUseExeDelays.state = 'normal'
            self.ids.tglUseExeFW.active = False
            self.ids.tglUseExeFW.state = 'normal'
            self.ids.tglUseExePinLevel.active = False
            self.ids.tglUseExePinLevel.state = 'normal'
            self.ids.tglUseExeReset.active = False
            self.ids.tglUseExeReset.state = 'normal'
            self.ids.tglUseExeBandwidth.active = False
            self.ids.tglUseExeBandwidth.state = 'normal'
            self.ids.tglUseExeInfo.active = False
            self.ids.tglUseExeInfo.state = 'normal'
            self.ids.tglUseExeSeekCyl.active = False
            self.ids.tglUseExeSeekCyl.state = 'normal'

    def ini_read(self, section, option, filespec):
        config = configparser.ConfigParser()

        if (len(config.read(filespec)) == 0):
            print("\nERROR - cannot open " + filespec + "\n")
            sys.exit(1)

        if (config.has_section(section) == False):
            print("\nERROR - section [" + section + "] does not exist in " + filespec + "\n")
            sys.exit(1)

        if (config.has_option(section, option) == False):
            print("\nERROR - option " + option + " does not exist in section [" + section + "]\n")
            sys.exit(1)

        print(config.get(section, option))

    def iniWriteFile(self):

        config = configparser.ConfigParser()

        # Miscellaneous
        config.add_section('gbMiscellaneous')
        if self.ids.tglUseExeRFD.state == "down" or self.ids.tglUseExeWTD.state == "down" \
                or self.ids.tglUseExeErase.state == "down" or self.ids.tglUseExeDelays.state == "down" \
                or self.ids.tglUseExeFW.state == "down" or self.ids.tglUseExePinLevel.state == "down" \
                or self.ids.tglUseExeReset.state == "down" or self.ids.tglUseExeBandwidth.state == "down":
            config.set('gbMiscellaneous', 'tglUseExeMode', 'True')
        else:
            config.set('gbMiscellaneous', 'tglUseExeMode', 'False')

        # read from disk
        config.add_section('gbReadFromDisk')
        config.set('gbReadFromDisk', 'txtCommandLineRFD', self.ids.txtCommandLineRFD.text)
        config.set('gbReadFromDisk', 'gw_RFDFilename', self.main_screen.gw_RFDFilename)
        config.set('gbReadFromDisk', 'gw_RFDFolder', self.main_screen.gw_RFDFolder)
        if self.ids.chkDoubleStepRFD.active:
            config.set('gbReadFromDisk', 'chkDoubleStepRFD', 'True')
        else:
            config.set('gbReadFromDisk', 'chkDoubleStepRFD', 'False')
        if self.ids.chkRevsPerTrack.active:
            config.set('gbReadFromDisk', 'chkRevsPerTrack',  'True')
        else:
            config.set('gbReadFromDisk', 'chkRevsPerTrack',  'False')
        config.set('gbReadFromDisk', 'txtRevsPerTrack', self.ids.txtRevsPerTrack.text)
        if self.ids.chkFirstCylToRead.active:
            config.set('gbReadFromDisk', 'chkFirstCylToRead', 'True')
        else:
            config.set('gbReadFromDisk', 'chkFirstCylToRead', 'False')
        config.set('gbReadFromDisk', 'txtFirstCylToRead', self.ids.txtFirstCylToRead.text)
        if self.ids.chkLastCylToRead.active:
            config.set('gbReadFromDisk', 'chkLastCylToRead', 'True')
        else:
            config.set('gbReadFromDisk', 'chkLastCylToRead', 'False')
        config.set('gbReadFromDisk', 'txtLastCylToRead', self.ids.txtLastCylToRead.text)
        if self.ids.chkSelectDriveRFD.active:
            config.set('gbReadFromDisk', 'chkSelectDriveRFD', 'True')
        else:
            config.set('gbReadFromDisk', 'chkSelectDriveRFD', 'False')
        config.set('gbReadFromDisk', 'txtSelectDriveRFD', self.ids.txtSelectDriveRFD.text)
        if self.ids.chkRateRFD.active:
            config.set('gbReadFromDisk', 'chkRateRFD', 'True')
        else:
            config.set('gbReadFromDisk', 'chkRateRFD', 'False')
        config.set('gbReadFromDisk', 'txtRateRFD', self.ids.txtRateRFD.text)
        if self.ids.chkRpmRFD.active:
            config.set('gbReadFromDisk', 'chkRpmRFD', 'True')
        else:
            config.set('gbReadFromDisk', 'chkRpmRFD', 'False')
        config.set('gbReadFromDisk', 'txtRpmRFD', self.ids.txtRpmRFD.text)
        if self.ids.tglSingleSidedRFD.state == "down":
            config.set('gbReadFromDisk', 'tglSingleSidedRFD', 'True')
        else:
            config.set('gbReadFromDisk', 'tglSingleSidedRFD', 'False')
        if self.ids.tglSingleSidedLegacyRFD.state == "down":
            config.set('gbReadFromDisk', 'tglSingleSidedLegacyRFD', 'True')
        else:
            config.set('gbReadFromDisk', 'tglSingleSidedLegacyRFD', 'False')

        # write to disk
        config.add_section('gbWriteToDisk')
        config.set('gbWriteToDisk', 'txtCommandLineWTD', self.ids.txtCommandLineWTD.text)
        config.set('gbWriteToDisk', 'gw_WTDFilename', self.main_screen.gw_WTDFilename)
        config.set('gbWriteToDisk', 'gw_WTDFolder', self.main_screen.gw_WTDFolder)
        if self.ids.chkAdjustSpeed.active:
            config.set('gbWriteToDisk', 'chkAdjustSpeed', 'True')
        else:
            config.set('gbWriteToDisk', 'chkAdjustSpeed', 'False')
        if self.ids.chkDoubleStepWTD.active:
            config.set('gbWriteToDisk', 'chkDoubleStepWTD', 'True')
        else:
            config.set('gbWriteToDisk', 'chkDoubleStepWTD', 'False')
        if self.ids.chkEraseEmptyWTD.active:
            config.set('gbWriteToDisk', 'chkEraseEmptyWTD', 'True')
        else:
            config.set('gbWriteToDisk', 'chkEraseEmptyWTD', 'False')
        if self.ids.chkFirstCylToWrite.active:
            config.set('gbWriteToDisk', 'chkFirstCylToWrite', 'True')
        else:
            config.set('gbWriteToDisk', 'chkFirstCylToWrite', 'False')
        config.set('gbWriteToDisk', 'txtFirstCylToWrite', self.ids.txtFirstCylToWrite.text)
        if self.ids.chkLastCylToWrite.active:
            config.set('gbWriteToDisk', 'chkLastCylToWrite', 'True')
        else:
            config.set('gbWriteToDisk', 'chkLastCylToWrite', 'False')
        config.set('gbWriteToDisk', 'txtLastCylToWrite', self.ids.txtLastCylToWrite.text)
        if self.ids.chkSelectDriveWTD.active:
            config.set('gbWriteToDisk', 'chkSelectDriveWTD', 'True')
        else:
            config.set('gbWriteToDisk', 'chkSelectDriveWTD', 'False')
        config.set('gbWriteToDisk', 'txtSelectDriveWTD', self.ids.txtSelectDriveWTD.text)
        if self.ids.tglSingleSidedWTD.state == "down":
            config.set('gbWriteToDisk', 'tglSingleSidedWTD', 'True')
        else:
            config.set('gbWriteToDisk', 'tglSingleSidedWTD', 'False')

        # erase disk
        config.add_section('gbEraseDisk')
        config.set('gbEraseDisk', 'txtCommandLineErase', self.ids.txtCommandLineErase.text)
        if self.ids.chkFirstCylToErase.active:
            config.set('gbEraseDisk', 'chkFirstCylToErase', 'True')
        else:
            config.set('gbEraseDisk', 'chkFirstCylToErase', 'False')
        config.set('gbEraseDisk', 'txtFirstCylToErase', self.ids.txtFirstCylToErase.text)
        if self.ids.chkLastCylToErase.active:
            config.set('gbEraseDisk', 'chkLastCylToErase', 'True')
        else:
            config.set('gbEraseDisk', 'chkLastCylToErase', 'False')
        config.set('gbEraseDisk', 'txtLastCylToErase', self.ids.txtLastCylToErase.text)
        if self.ids.chkSelectDriveErase.active:
            config.set('gbEraseDisk', 'chkSelectDriveErase', 'True')
        else:
            config.set('gbEraseDisk', 'chkSelectDriveErase', 'False')
        config.set('gbEraseDisk', 'txtSelectDriveErase', self.ids.txtSelectDriveErase.text)
        if self.ids.tglSingleSidedErase.state == "down":
            config.set('gbEraseDisk', 'tglSingleSidedErase', 'True')
        else:
            config.set('gbEraseDisk', 'tglSingleSidedErase', 'False')

        # set delays
        config.add_section('gbSetDelays')
        config.set('gbSetDelays', 'txtCommandLineDelays', self.ids.txtCommandLineDelays.text)
        if self.ids.chkDelayAfterSelect.active:
            config.set('gbSetDelays', 'chkDelayAfterSelect', 'True')
        else:
            config.set('gbSetDelays', 'chkDelayAfterSelect', 'False')
        config.set('gbSetDelays', 'txtDelayAfterSelect', self.ids.txtDelayAfterSelect.text)
        if self.ids.chkDelayBetweenSteps.active:
            config.set('gbSetDelays', 'chkDelayBetweenSteps', 'True')
        else:
            config.set('gbSetDelays', 'chkDelayBetweenSteps', 'False')
        config.set('gbSetDelays', 'txtDelayBetweenSteps', self.ids.txtDelayBetweenSteps.text)
        if self.ids.chkSettleDelayAfterSeek.active:
            config.set('gbSetDelays', 'chkSettleDelayAfterSeek', 'True')
        else:
            config.set('gbSetDelays', 'chkSettleDelayAfterSeek', 'False')
        config.set('gbSetDelays', 'txtSettleDelayAfterSeek', self.ids.txtSettleDelayAfterSeek.text)
        if self.ids.chkDelayAfterMotorOn.active:
            config.set('gbSetDelays', 'chkDelayAfterMotorOn', 'True')
        else:
            config.set('gbSetDelays', 'chkDelayAfterMotorOn', 'False')
        config.set('gbSetDelays', 'txtDelayAfterMotorOn', self.ids.txtDelayAfterMotorOn.text)
        if self.ids.chkDelayUntilAutoDeselect.active:
            config.set('gbSetDelays', 'chkDelayUntilAutoDeselect', 'True')
        else:
            config.set('gbSetDelays', 'chkDelayUntilAutoDeselect', 'False')
        config.set('gbSetDelays', 'txtDelayUntilAutoDeselect', self.ids.txtDelayUntilAutoDeselect.text)

        # update firmware
        config.add_section('gbUpdateFirmware')
        config.set('gbUpdateFirmware', 'txtCommandLineFirmware', self.ids.txtCommandLineFirmware.text)
        config.set('gbUpdateFirmware', 'gw_UpdateFWFilename', self.main_screen.gw_UpdateFWFilename)
        config.set('gbUpdateFirmware', 'gw_UpdateFWFolder', self.main_screen.gw_UpdateFWFolder)
        if self.ids.tglBootloader.state == "down":
            config.set('gbUpdateFirmware', 'tglBootloader', "True")
        else:
            config.set('gbUpdateFirmware', 'tglBootloader', "False")

        # pin level
        config.add_section('gbPinLevel')
        if self.ids.chkHighLevel.active:
            config.set('gbPinLevel', 'chkHighLevel', 'True')
        else:
            config.set('gbPinLevel', 'chkHighLevel', 'False')
        if self.ids.chkLowLevel.active:
            config.set('gbPinLevel', 'chkLowLevel', 'True')
        else:
            config.set('gbPinLevel', 'chkLowLevel', 'False')
        config.set('gbPinLevel', 'txtPinLevel', self.ids.txtPinLevel.text)
        config.set('gbPinLevel', 'txtCommandLinePinLevel', self.ids.txtCommandLinePinLevel.text)

        # seek cylinder
        config.add_section('gbSeekCyl')
        if self.ids.chkSelectDriveSeekCyl.active:
            config.set('gbSeekCyl', 'chkSelectDriveSeekCyl', 'True')
        else:
            config.set('gbSeekCyl', 'chkSelectDriveSeekCyl', 'False')
        config.set('gbSeekCyl', 'txtSelectDriveSeekCyl', self.ids.txtSelectDriveSeekCyl.text)
        config.set('gbSeekCyl', 'txtCommandLineSeekCyl', self.ids.txtCommandLineSeekCyl.text)
        config.set('gbSeekCyl', 'txtSeekCyl', self.ids.txtSeekCyl.text)

        # reset - nothing to do
        # bandwidth - nothing to do
        # info - nothing to do

        # write the file
        with open(self.gw_iniFilespec, 'w') as configfile:
            config.write(configfile)

    def iniReadFile(self):
        config = configparser.ConfigParser()
        if (len(config.read(self.gw_iniFilespec)) == 0):
            print("\nDoesn't yet exist " + self.gw_iniFilespec + "\n")
            return

        try:

            # miscellaneous
            state = config.get('gbMiscellaneous', 'tglUseExeMode')
            self.set_exe_mode(state)
            self.main_screen.gw_RFDFilename = config.get('gbReadFromDisk', 'gw_RFDFilename')
            self.main_screen.gw_RFDFolder = config.get('gbReadFromDisk', 'gw_RFDFolder')

            # read from disk
            state = config.get('gbReadFromDisk', 'chkDoubleStepRFD')
            if state == 'True':
                self.ids.chkDoubleStepRFD.active = True
                self.ids.chkDoubleStepRFD.state = 'down'
            state = config.get('gbReadFromDisk', 'chkRevsPerTrack')
            if state == 'True':
                self.ids.chkRevsPerTrack.active = True
                self.ids.chkRevsPerTrack.state = 'down'
            self.ids.txtRevsPerTrack.text = config.get('gbReadFromDisk', 'txtRevsPerTrack')
            state = config.get('gbReadFromDisk', 'chkFirstCylToRead')
            if state == 'True':
                self.ids.chkFirstCylToRead.active = True
                self.ids.chkFirstCylToRead.state = 'down'
            self.ids.txtFirstCylToRead.text = config.get('gbReadFromDisk', 'txtFirstCylToRead')
            state = config.get('gbReadFromDisk', 'chkLastCylToRead')
            if state == 'True':
                self.ids.chkLastCylToRead.active = True
                self.ids.chkLastCylToRead.state = 'down'
            self.ids.txtLastCylToRead.text = config.get('gbReadFromDisk', 'txtLastCylToRead')
            state = config.get('gbReadFromDisk', 'chkSelectDriveRFD')
            if state == 'True':
                self.ids.chkSelectDriveRFD.active = True
                self.ids.chkSelectDriveRFD.state = 'down'
            self.ids.txtSelectDriveRFD.text = config.get('gbReadFromDisk', 'txtSelectDriveRFD')
            state = config.get('gbReadFromDisk', 'chkRateRFD')
            if state == 'True':
                self.ids.chkRateRFD.active = True
                self.ids.chkRateRFD.state = 'down'
            self.ids.txtRateRFD.text = config.get('gbReadFromDisk', 'txtRateRFD')
            state = config.get('gbReadFromDisk', 'chkRpmRFD')
            if state == 'True':
                self.ids.chkRpmRFD.active = True
                self.ids.chkRpmRFD.state = 'down'
            self.ids.txtRpmRFD.text = config.get('gbReadFromDisk', 'txtRpmRFD')
            state = config.get('gbReadFromDisk', 'tglSingleSidedRFD')
            if state == 'True':
                self.ids.tglSingleSidedRFD.active = True
                self.ids.tglSingleSidedRFD.state = 'down'
            state = config.get('gbReadFromDisk', 'tglSingleSidedLegacyRFD')
            if state == 'True':
                self.ids.tglSingleSidedLegacyRFD.active = True
                self.ids.tglSingleSidedLegacyRFD.state = 'down'

            # write to disk
            self.main_screen.gw_WTDFilename = config.get('gbWriteToDisk', 'gw_WTDFilename')
            self.main_screen.gw_WTDFolder = config.get('gbWriteToDisk', 'gw_WTDFolder')
            state = config.get('gbWriteToDisk', 'chkAdjustSpeed')
            if state == 'True':
                self.ids.chkAdjustSpeed.active = True
                self.ids.chkAdjustSpeed.state = 'down'
            state = config.get('gbWriteToDisk', 'chkDoubleStepWTD')
            if state == 'True':
                self.ids.chkDoubleStepWTD.active = True
                self.ids.chkDoubleStepWTD.state = 'down'
            state = config.get('gbWriteToDisk', 'chkEraseEmptyWTD')
            if state == 'True':
                self.ids.chkEraseEmptyWTD.active = True
                self.ids.chkEraseEmptyWTD.state = 'down'
            state = config.get('gbWriteToDisk', 'chkFirstCylToWrite')
            if state == 'True':
                self.ids.chkFirstCylToWrite.active = True
                self.ids.chkFirstCylToWrite.state = 'down'
            self.ids.txtFirstCylToWrite.text = config.get('gbWriteToDisk', 'txtFirstCylToWrite')
            state = config.get('gbWriteToDisk', 'chkLastCylToWrite')
            if state == 'True':
                self.ids.chkLastCylToWrite.active = True
                self.ids.chkLastCylToWrite.state = 'down'
            self.ids.txtLastCylToWrite.text = config.get('gbWriteToDisk', 'txtLastCylToWrite')
            state = config.get('gbWriteToDisk', 'chkSelectDriveWTD')
            if state == 'True':
                self.ids.chkSelectDriveWTD.active = True
                self.ids.chkSelectDriveWTD.state = 'down'
            self.ids.txtSelectDriveWTD.text = config.get('gbWriteToDisk', 'txtSelectDriveWTD')
            state = config.get('gbWriteToDisk', 'tglSingleSidedWTD')
            if state == 'True':
                self.ids.tglSingleSidedWTD.active = True
                self.ids.tglSingleSidedWTD.state = 'down'

            # erase disk
            state = config.get('gbEraseDisk', 'chkFirstCylToErase')
            if state == 'True':
                self.ids.chkFirstCylToErase.active = True
                self.ids.chkFirstCylToErase.state = 'down'
            self.ids.txtFirstCylToErase.text = config.get('gbEraseDisk', 'txtFirstCylToErase')
            state = config.get('gbEraseDisk', 'chkLastCylToErase')
            if state == 'True':
                self.ids.chkLastCylToErase.active = True
                self.ids.chkLastCylToErase.state = 'down'
            self.ids.txtLastCylToErase.text = config.get('gbEraseDisk', 'txtLastCylToErase')
            state = config.get('gbEraseDisk', 'chkSelectDriveErase')
            if state == 'True':
                self.ids.chkSelectDriveErase.active = True
                self.ids.chkSelectDriveErase.state = 'down'
            self.ids.txtSelectDriveErase.text = config.get('gbEraseDisk', 'txtSelectDriveErase')
            state = config.get('gbEraseDisk', 'tglSingleSidedErase')
            if state == 'True':
                self.ids.tglSingleSidedErase.active = True
                self.ids.tglSingleSidedErase.state = 'down'

            # set delays
            self.ids.txtCommandLineDelays.text = config.get('gbSetDelays', 'txtCommandLineDelays')
            state = config.get('gbSetDelays', 'chkDelayAfterSelect')
            if state == 'True':
                self.ids.chkDelayAfterSelect.active = True
                self.ids.chkDelayAfterSelect.state = 'down'
            self.ids.txtDelayAfterSelect.text = config.get('gbSetDelays', 'txtDelayAfterSelect')
            state = config.get('gbSetDelays', 'chkDelayBetweenSteps')
            if state == 'True':
                self.ids.chkDelayBetweenSteps.active = True
                self.ids.chkDelayBetweenSteps.state = 'down'
            self.ids.txtDelayBetweenSteps.text = config.get('gbSetDelays', 'txtDelayBetweenSteps')

            state = config.get('gbSetDelays', 'chkSettleDelayAfterSeek')
            if state == 'True':
                self.ids.chkSettleDelayAfterSeek.active = True
                self.ids.chkSettleDelayAfterSeek.state = 'down'
            self.ids.txtSettleDelayAfterSeek.text = config.get('gbSetDelays', 'txtSettleDelayAfterSeek')
            state = config.get('gbSetDelays', 'chkDelayAfterMotorOn')
            if state == 'True':
                self.ids.chkDelayAfterMotorOn.active = True
                self.ids.chkDelayAfterMotorOn.state = 'down'
            self.ids.txtDelayAfterMotorOn.text = config.get('gbSetDelays', 'txtDelayAfterMotorOn')
            state = config.get('gbSetDelays', 'chkDelayUntilAutoDeselect')
            if state == 'True':
                self.ids.chkDelayUntilAutoDeselect.active = True
                self.ids.chkDelayUntilAutoDeselect.state = 'down'
            self.ids.txtDelayUntilAutoDeselect.text = config.get('gbSetDelays', 'txtDelayUntilAutoDeselect')

            # update firmware
            self.main_screen.gw_UpdateFWFilename = config.get('gbUpdateFirmware', 'gw_UpdateFWFilename')
            self.main_screen.gw_UpdateFWFolder = config.get('gbUpdateFirmware', 'gw_UpdateFWFolder')
            state = config.get('gbUpdateFirmware', 'tglBootloader')
            if state == 'True':
                self.ids.tglBootloader.active = True
                self.ids.tglBootloader.state = "down"

            # pin level
            self.ids.txtCommandLinePinLevel.text = config.get('gbPinLevel', 'txtCommandLinePinLevel')
            self.ids.txtPinLevel.text = config.get('gbPinLevel', 'txtPinLevel')
            state = config.get('gbPinLevel', 'chkHighLevel')
            if state == 'True':
                self.ids.chkHighLevel.active = True
                self.ids.chkHighLevel.state = 'down'
            state = config.get('gbPinLevel', 'chkLowLevel')
            if state == 'True':
                self.ids.chkLowLevel.active = True
                self.ids.chkLowLevel.state = 'down'

            # seek cylinder
            self.ids.txtCommandLineSeekCyl.text = config.get('gbSeekCyl', 'txtCommandLineSeekCyl')
            self.ids.txtSeekCyl.text = config.get('gbSeekCyl', 'txtSeekCyl')
            state = config.get('gbSeekCyl', 'chkSelectDriveSeekCyl')
            if state == 'True':
                self.ids.chkSelectDriveSeekCyl.active = True
                self.ids.chkSelectDriveSeekCyl.state = 'down'
            self.ids.txtSelectDriveSeekCyl.text = config.get('gbSeekCyl', 'txtSelectDriveSeekCyl')

            # reset - nothing to do
            # bandwidth - nothing to do
            # info - nothing to do

        except:
            # assume one of the entries don't exist in an old format file
            # so lets delete the old on and start over
            print("\nDeleting old file " + self.gw_iniFilespec + "\n")
            os.remove(self.gw_iniFilespec)

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
        self.dialog_mode = 0  # 0 = RFD, 1 = WTD, 2 = UpdateFirmware

    def set_dialog_mode(self, mode):
        self.dialog_mode = mode

    def get_dialog_mode(self):
        return self.dialog_mode

    def set_file_name(self, fn):
        if len(fn) == 0:
            return
        head, tail = ntpath.split(fn)
        mode = self.get_dialog_mode()
        print('mode = ' + str(mode))
        if mode == 0:  # RFD
            self.main_screen.gw_RFDFolder = head
            self.main_screen.gw_RFDFilename = tail
        if mode == 1:  # WTD
            self.main_screen.gw_WTDFolder = head
            self.main_screen.gw_WTDFilename = tail
        if mode == 2:  # FW
            self.main_screen.gw_UpdateFWFolder = head
            self.main_screen.gw_UpdateFWFilename = tail
        self.main_screen.gw_dirty = True

class FileUpdateDialogScreen(Screen):

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.main_screen = MainScreen
        self.dialog_mode = 0  # 0 = RFD, 1 = WTD, 2 = UpdateFirmware

    def set_dialog_mode(self, mode):
        self.dialog_mode = mode

    def get_dialog_mode(self):
        return self.dialog_mode

    def set_file_name(self, fn):
        if len(fn) == 0:
            return
        head, tail = ntpath.split(fn)
        mode = self.get_dialog_mode()
        print('mode = ' + str(mode))
        if mode == 0:  # RFD
            self.main_screen.gw_RFDFolder = head
            self.main_screen.gw_RFDFilename = tail
        if mode == 1:  # WTD
            self.main_screen.gw_WTDFolder = head
            self.main_screen.gw_WTDFilename = tail
        if mode == 2:  # FW
            self.main_screen.gw_UpdateFWFolder = head
            self.main_screen.gw_UpdateFWFilename = tail
        self.main_screen.gw_dirty = True

class FolderDialogScreen(Screen):

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.main_screen = MainScreen
        self.dialog_mode = 0  # 0 = RFD, 1 = WTD, 2 = UpdateFirmware

    def set_dialog_mode(self, mode):
        self.dialog_mode = mode

    def get_dialog_mode(self):
        return self.dialog_mode

    def set_folder_name(self, fn):
        if len(fn) == 0:
            return
        mode = self.get_dialog_mode()
        print('mode = ' + str(mode))
        if mode == 0:  # RFD
            self.main_screen.gw_RFDFolder = fn
        if mode == 1:  # WTD
            self.main_screen.gw_WTDFolder = fn
        if mode == 2:  # FW
            self.main_screen.gw_UpdateFWFolder = fn
        self.main_screen.gw_dirty = True

class ErrorScreen(Screen):
    pass

GUI = Builder.load_file("gui.kv")
class MainApp(App):
    title = "GreaseweazleGUI v0.45 / Host Tools v0.21 - by Don Mankin"

    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        return GUI
    def change_screen(self, screen_name):
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name

    def on_start(self, **kwargs):
        main_screen = self.root.ids['main_screen']
        main_screen.iniReadFile()

    def on_request_close(self, *args):
        main_screen = self.root.ids['main_screen']
        main_screen.iniWriteFile()
        if main_screen.checkIfProcessRunningByScript("gw.py"):
            self.root.ids['screen_manager'].current = 'error_screen'
            return True
        else:
            return False

MainApp().run()

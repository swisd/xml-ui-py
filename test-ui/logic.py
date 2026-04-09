from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QLineEdit


#
# def submit(ui):
#     name = ui.widgets['name_in'].text()
#     age = ui.widgets['age_in'].value()
#
#     if not name:
#         ui.widgets['status_label'].setText("❌ Please enter a name!")
#         return
#
#     ui.widgets['status_label'].setText(f"✅ Submitted {name} ({age})")
#     ui.widgets['progress'].setValue(100)

def show_info(ui):
    msg = QMessageBox()
    msg.setText("This UI was generated entirely from XML!")
    msg.setInformativeText("It uses dynamic attribute mapping to call PyQt6 methods.")
    msg.exec()
    
    # Update the status label we named in XML
    ui.widgets['status_label'].setText("User clicked the button!")
    set_value(ui)
    
def set_value(ui):
    # 1. Grab the widget by its name
    lcd = ui.widgets.get('main_display')
    
    if lcd:
        # 2. Set the value
        # You can use .display() for integers or floats
        lcd.setDigitCount(5)
        lcd.display(123.45)
        
        # Or even strings (if they fit the digit count)
        # lcd.display("12:34")
        
def set_closable(ui):
    tabs = ui.widgets.get('tabs')
    tabs.setTabsClosable(True)

def set_unclosable(ui):
    tabs = ui.widgets.get('tabs')
    tabs.setTabsClosable(False)
    
def set_horiz_slider(ui):
    slider = ui.widgets.get('volume_slider')
    slider.setOrientation(Qt.Orientation.Horizontal)
    
def set_passview(ui):
    textbox = ui.widgets.get('pass_in')
    echmode = textbox.echoMode()
    if echmode == QLineEdit.EchoMode.Normal:
     textbox.setEchoMode(QLineEdit.EchoMode.Password)
    else:
     textbox.setEchoMode(QLineEdit.EchoMode.Normal)
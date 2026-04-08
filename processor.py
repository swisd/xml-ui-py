import sys
import os
import importlib.util
import xml.etree.ElementTree as ET
from PyQt6 import QtWidgets


class XMLGui(QtWidgets.QWidget):
    def __init__(self, xml_string, logic_module=None):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.widgets = {}
        self.logic = logic_module  # Our "Code-behind"
        self.parse_xml(xml_string)
    
    def parse_xml(self, xml_string):
        root = ET.fromstring(xml_string)
        self.setWindowTitle(root.attrib.get('title', 'XML App'))
        
        for element in root:
            tag_name = element.tag
            attrs = element.attrib
            
            # Lookup widget class in QtWidgets
            widget_class = getattr(QtWidgets, tag_name, None)
            
            if widget_class:
                widget = widget_class()
                
                # Apply attributes
                if 'text' in attrs and hasattr(widget, 'setText'):
                    widget.setText(attrs['text'])
                if 'placeholder' in attrs and hasattr(widget, 'setPlaceholderText'):
                    widget.setPlaceholderText(attrs['placeholder'])
                
                # Dynamic Event Binding
                if 'action' in attrs and hasattr(widget, 'clicked'):
                    action_name = attrs['action']
                    # Look for the function in the external logic module first,
                    # then fall back to this class
                    callback = getattr(self.logic, action_name, getattr(self, action_name, None))
                    
                    if callback:
                        # Pass 'self' (the UI) so the logic script can access widgets
                        widget.clicked.connect(lambda checked, cb=callback: cb(self))
                
                # Store by name for easy access via self.widgets['name']
                name = attrs.get('name')
                if name:
                    self.widgets[name] = widget
                
                self.layout.addWidget(widget)


def load_logic_file(path):
    """Dynamically imports a python file as a module."""
    module_name = "custom_logic"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <ui.xml> <logic.py>")
        sys.exit(1)
    
    xml_path = sys.argv[1]
    logic_path = sys.argv[2]
    
    # Load files
    with open(xml_path, 'r') as f:
        xml_data = f.read()
    
    logic_mod = load_logic_file(logic_path)
    
    app = QtWidgets.QApplication(sys.argv)
    window = XMLGui(xml_data, logic_mod)
    window.show()
    sys.exit(app.exec())
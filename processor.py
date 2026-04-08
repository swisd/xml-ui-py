import sys
import importlib.util
import xml.etree.ElementTree as ET
from PyQt6 import QtWidgets, QtCore


class XMLGui(QtWidgets.QWidget):
    def __init__(self, xml_string):
        super().__init__()
        self.widgets = {}
        self.modules = {}  # Stores imported python files
        self.parse_xml(xml_string)
    
    def _load_module(self, name, path):
        """Helper to dynamically import a file."""
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.modules[name] = mod
        except Exception as e:
            print(f"Failed to import {name} from {path}: {e}")
    
    def parse_xml(self, xml_string):
        root = ET.fromstring(xml_string)
        self.setWindowTitle(root.attrib.get('title', 'XML App'))
        
        # 1. Process Imports first
        for imp in root.findall('Import'):
            name = imp.attrib.get('name')
            path = imp.attrib.get('path')
            if name and path:
                self._load_module(name, path)
        
        # 2. Setup Layout
        layout = QtWidgets.QGridLayout() if root.tag == "GridLayout" else QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        # 3. Build UI (skipping Import tags)
        self.build_ui(root, layout)
    
    def build_ui(self, parent_element, layout):
        for element in parent_element:
            if element.tag == "Import": continue
            
            tag_name = element.tag
            attrs = element.attrib
            
            widget_class = getattr(QtWidgets, tag_name, None)
            if not widget_class: continue
            
            widget = widget_class()
            
            # Attribute Mapping
            for key, value in attrs.items():
                if key in ['row', 'col', 'rowSpan', 'colSpan', 'action', 'name']: continue
                
                setter = getattr(widget, f"set{key[0].upper()}{key[1:]}", None)
                if setter:
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    try:
                        setter(value)
                    except:
                        pass
            
            # Scoped Action Binding (e.g., action="my_logic.submit")
            if 'action' in attrs:
                action_path = attrs['action'].split('.')
                if len(action_path) == 2:
                    mod_name, func_name = action_path
                    mod = self.modules.get(mod_name)
                    callback = getattr(mod, func_name, None)
                    if callback and hasattr(widget, 'clicked'):
                        widget.clicked.connect(lambda checked, cb=callback: cb(self))
            
            # Grid Logic
            if isinstance(layout, QtWidgets.QGridLayout):
                r, c = int(attrs.get('row', 0)), int(attrs.get('col', 0))
                rs, cs = int(attrs.get('rowSpan', 1)), int(attrs.get('colSpan', 1))
                layout.addWidget(widget, r, c, rs, cs)
            else:
                layout.addWidget(widget)
            
            if 'name' in attrs:
                self.widgets[attrs['name']] = widget


if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        app = QtWidgets.QApplication(sys.argv)
        window = XMLGui(f.read())
        window.show()
        sys.exit(app.exec())
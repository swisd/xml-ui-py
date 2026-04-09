import sys
import importlib.util
import xml.etree.ElementTree as ET
from PyQt6 import QtWidgets, QtCore


class XMLGui(QtWidgets.QMainWindow):
    def __init__(self, xml_string):
        super().__init__()
        self.widgets = {}
        self.modules = {}
        self.parse_xml(xml_string)
        self.init_func = None
    
    def _load_module(self, name, path):
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.modules[name] = mod
        except Exception as e:
            print(f"Error loading module {name}: {e}")
    
    def parse_xml(self, xml_string):
        print("Parsing XML")
        root = ET.fromstring(xml_string)
        self.setWindowTitle(root.attrib.get('title', 'PyQt6 App'))
        
        init_attr = root.get("onInit")
        
        if init_attr:
            # Split "logic.initialize_ui" -> ["logic", "initialize_ui"]
            module_name, func_name = init_attr.split('.')
            
            self.init_func = (module_name, func_name)
            # Get the function from your imported modules
            

        
        for imp in root.findall('Import'):
            self._load_module(imp.attrib.get('name'), imp.attrib.get('path'))
        
        layout_node = root.find('Layout')
        if layout_node is not None:
            central_widget = QtWidgets.QWidget()
            self.setCentralWidget(central_widget)
            lt_type = layout_node.attrib.get('type', 'Vertical')
            layout = QtWidgets.QGridLayout() if lt_type == 'Grid' else QtWidgets.QVBoxLayout()
            if lt_type == 'Grid':
                stretch_val = layout_node.attrib.get('stretch')
                if stretch_val:
                    print(f"strect val {stretch_val}")
                    # Convert "3,7" into [3, 7]
                    columns = [int(s) for s in stretch_val.split(',')]
                    for i, s in enumerate(columns):
                        layout.setColumnStretch(i, s)
            central_widget.setLayout(layout)
            self.build_ui(layout_node, layout)
    
    def add_tree_items(self, xml_element, parent_obj):
        """Recursively adds Items to QTreeWidget or QTreeWidgetItem."""
        for item_node in xml_element.findall('Item'):
            values = item_node.attrib.get('values', 'New Item').split(',')
            # In PyQt, the first arg is the parent (Tree or Item)
            new_item = QtWidgets.QTreeWidgetItem(parent_obj, values)
            
            # Recursively add children to THIS item
            self.add_tree_items(item_node, new_item)
    
    def build_ui(self, parent_element, current_layout):
        print("Building UI")
        for element in parent_element:
            tag_name = element.tag
            attrs = element.attrib
            
            # Skip non-widget tags
            if tag_name in ['Import', 'Item', 'Tab', 'Page']: continue
            
            # --- NEW: Handle Nested Layouts ---
            if tag_name == 'Layout':
                lt_type = attrs.get('type', 'Vertical')
                if lt_type == 'Grid':
                    new_layout = QtWidgets.QGridLayout()
                    # --- NEW: Handle Stretch ---
                    stretch_val = attrs.get('stretch')
                    if stretch_val:
                        print(f"strect val {stretch_val}")
                        # Convert "3,7" into [3, 7]
                        columns = [int(s) for s in stretch_val.split(',')]
                        for i, s in enumerate(columns):
                            new_layout.setColumnStretch(i, s)
                            
                elif lt_type == 'Horizontal':
                    new_layout = QtWidgets.QHBoxLayout()
                else:
                    new_layout = QtWidgets.QVBoxLayout()
                
                # Nest the layout
                if isinstance(current_layout, QtWidgets.QGridLayout):
                    r, c = int(attrs.get('row', 0)), int(attrs.get('col', 0))
                    rs, cs = int(attrs.get('rowSpan', 1)), int(attrs.get('colSpan', 1))
                    current_layout.addLayout(new_layout, r, c, rs, cs)
                else:
                    current_layout.addLayout(new_layout)
                
                # Recursively build inside this new layout
                self.build_ui(element, new_layout)
                continue  # Skip the widget logic for this tag
            
            widget_class = getattr(QtWidgets, tag_name, None)
            if not widget_class or not issubclass(widget_class, QtWidgets.QWidget):
                continue
            
            widget = widget_class()
            
            # 1. Apply Attributes
            for key, value in attrs.items():
                if key in ['row', 'col', 'rowSpan', 'colSpan', 'action', 'name']: continue
                setter = getattr(widget, f"set{key[0].upper()}{key[1:]}", None)
                if setter:
                    val = True if value.lower() == 'true' else False if value.lower() == 'false' else int(
                        value) if value.isdigit() else value
                    try:
                        setter(val)
                    except:
                        pass
            
            # Special Header Logic for Trees
            if isinstance(widget, QtWidgets.QTreeWidget) and 'headers' in attrs:
                widget.setHeaderLabels(attrs['headers'].split(','))

            # Bind Actions
            if 'action' in attrs and '.' in attrs['action']:
                mod_n, func_n = attrs['action'].split('.')
                mod = self.modules.get(mod_n)
                if mod and hasattr(widget, 'clicked'):
                    callback = getattr(mod, func_n, None)
                    if callback: widget.clicked.connect(lambda checked, cb=callback: cb(self))
            
            # 3. Add to Current Layout
            if isinstance(current_layout, QtWidgets.QGridLayout):
                r, c = int(attrs.get('row', 0)), int(attrs.get('col', 0))
                rs, cs = int(attrs.get('rowSpan', 1)), int(attrs.get('colSpan', 1))
                current_layout.addWidget(widget, r, c, rs, cs)
            
            else:
                current_layout.addWidget(widget)
            
            if 'name' in attrs: self.widgets[attrs['name']] = widget
            
            # 4. Handle Internal Children / Complex Logic
            if len(element) > 0:
                if isinstance(widget, QtWidgets.QTreeWidget):
                    self.add_tree_items(element, widget)
                    widget.expandAll() # Ensure they are visible
                elif isinstance(widget, (QtWidgets.QTabWidget, QtWidgets.QToolBox)):
                    for child in element:
                        title = child.attrib.get('title', 'Page')
                        page = QtWidgets.QWidget()
                        page_layout = QtWidgets.QVBoxLayout(page)
                        if isinstance(widget, QtWidgets.QTabWidget):
                            widget.addTab(page, title)
                        else:
                            widget.addItem(page, title)
                        self.build_ui(child, page_layout)
                
                # Specialized: Lists and Combos
                elif isinstance(widget, (QtWidgets.QListWidget, QtWidgets.QComboBox)):
                    for item in element.findall('Item'):
                        widget.addItem(item.attrib.get('text', ''))
                
                # Specialized: Trees
                elif isinstance(widget, QtWidgets.QTreeWidget):
                    widget.setHeaderLabels(attrs.get('headers', 'Column').split(','))
                    for item in element.findall('Item'):
                        QtWidgets.QTreeWidgetItem(widget, item.attrib.get('values', '').split(','))
                
                # Standard: GroupBoxes and Frames
                else:
                    child_layout = QtWidgets.QVBoxLayout(widget)
                    self.build_ui(element, child_layout)
                    
                    
    def call_init_func(self):
        if self.init_func is not None:
            IF = getattr(self.modules[self.init_func[0]], self.init_func[1])
            IF(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    with open(sys.argv[1], 'r') as f:
        window = XMLGui(f.read())
        window.call_init_func()
        window.show()
        sys.exit(app.exec())
import os

from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtCore import Qt

# Configuration: Point this to your documentation folder
DOCS_PATH = "./docs/doc-dir/"


def initialize_ui(ui):
    """
    Called when the UI is first loaded to populate the tree.
    """
    help_tree = ui.widgets["help_tree"]
    help_tree.clear()
    populate_tree(help_tree.invisibleRootItem(), DOCS_PATH)
    # Connect the selection signal
    help_tree.itemSelectionChanged.connect(lambda: load_page(ui))


def populate_tree(parent_item, path):
    """
    Recursively parses the directory structure and adds .hlp files to the tree.
    """
    for entry in os.scandir(path):
        if entry.is_dir():
            # Create a folder category
            node = QTreeWidgetItem(parent_item, [entry.name])
            node.setData(0, Qt.ItemDataRole.UserRole, "folder")
            populate_tree(node, entry.path)
        elif entry.name.endswith(".docs"):
            # Create a file leaf
            leaf = QTreeWidgetItem(parent_item, [entry.name])
            # Store the full path in UserRole so we can open it later
            leaf.setData(0, Qt.ItemDataRole.UserRole, entry.path)


def load_page(ui):
    """
    Triggered when a user clicks a tree item. Reads the .hlp file.
    """
    help_tree = ui.widgets["help_tree"]
    doc_viewer = ui.widgets["doc_viewer"]
    breadcrumb_label = ui.widgets["breadcrumb_label"]
    word_count = ui.widgets["word_count"]
    selected = help_tree.selectedItems()
    if not selected:
        return
    
    file_path = selected[0].data(0, Qt.ItemDataRole.UserRole)
    
    if file_path and file_path != "folder":
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                doc_viewer.setPlainText(content)
                breadcrumb_label.setText(f"Reading: {selected[0].text(0)}")
                
                # Update word count logic
                words = len(content.split())
                word_count.setText(f"Words: {words}")
        except Exception as e:
            doc_viewer.setPlainText(f"Error loading file: {e}")


def filter_tree(ui):
    """
    Filters the tree based on the search bar input.
    """
    search_filter = ui.widgets["search_filter"]
    help_tree = ui.widgets["help_tree"]
    search_text = search_filter.text().lower()
    items = help_tree.findItems("", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive)
    
    for item in items:
        # Hide items that don't match the search
        item.setHidden(search_text not in item.text(0).lower())


def collapse_all(ui):
    """
    Utility to tidy up the sidebar.
    """
    help_tree = ui.widgets["help_tree"]
    help_tree.collapseAll()


def copy_path(ui):
    """
    Copies the current file path to clipboard.
    """
    help_tree = ui.widgets["help_tree"]
    selected = help_tree.selectedItems()
    if selected:
        path = selected[0].data(0, Qt.ItemDataRole.UserRole)
        if path != "folder":
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(path)


def zoom_in(ui):
    doc_viewer = ui.widgets["doc_viewer"]
    doc_viewer.zoomIn(1)


def zoom_out(ui):
    doc_viewer = ui.widgets["doc_viewer"]
    doc_viewer.zoomOut(1)
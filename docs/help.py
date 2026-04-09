def on_selection_changed():
    selected_items = ui.help_tree.selectedItems()
    if not selected_items:
        return
    
    item = selected_items[0]
    # Retrieve the filepath we stored in the item's hidden data
    file_path = item.data(0, Qt.ItemDataRole.UserRole)
    
    if file_path and file_path.endswith(".hlp"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            ui.doc_viewer.setPlainText(content)
            ui.breadcrumb_label.setText(f"Reading: {item.text(0)}")
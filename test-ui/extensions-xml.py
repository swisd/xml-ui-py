def on_submit(self):
    # Access widget by name defined in XML
    user_input = self.widgets['input_field'].text()
    print(f"Submitted: {user_input}")


def handle_click(ui):
    # Retrieve a widget by the 'name' attribute defined in XML
    field = ui.widgets.get('username_field')
    field2 = ui.widgets.get('out_field')
    if field:
        print(f"Logic file received input: {field.text()}")
        field2.text = field.text()
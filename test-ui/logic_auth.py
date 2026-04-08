def verify(ui):
    user = ui.widgets['user_field'].text()
    if user == "admin":
        ui.widgets['status'].setText("Success!")
    else:
        ui.widgets['status'].setText("Access Denied")
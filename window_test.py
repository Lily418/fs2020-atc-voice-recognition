from pywinauto.application import Application
import pywinauto


app = Application(backend="uia").connect(title_re=".*Microsoft Flight Simulator.*")
print(app.window(handle=pywinauto.findwindows.find_window(title="ATC")).capture_as_image().save("atc.png", "PNG"))
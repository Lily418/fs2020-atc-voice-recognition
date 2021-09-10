from pywinauto.application import Application


app = Application(backend="uia").connect(title_re=".*Firefox.*")
print(app.windows()[0])
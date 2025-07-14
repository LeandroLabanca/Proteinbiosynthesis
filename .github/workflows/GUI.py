import sys
from PyQt5.QtCore import QSize,Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ProteinBioSynthesis")
        button = QPushButton("Press me")
        button.setCheckable(True)
        button.clicked.connect(self.button_clicked)
        button.clicked.connect(self.button_toggled)

        self.setCentralWidget(button)
        self.setMinimumSize(1920, 1080)
        self.setMaximumSize(3840, 2160)

    def button_clicked(self):
        print("Button clicked")

    def button_toggled(self, checked):
        print("Button toggled", checked)




app=QApplication(sys.argv)

window=MainWindow()
window.show()
app.exec_()

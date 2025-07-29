import sys
from PyQt5.QtWidgets import (
QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QComboBox, QRadioButton, QButtonGroup, QMessageBox
)

class Biological_Sequence_Input(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.seq_type = QComboBox()
        self.seq_type.addItems([
            "Coding Sequence DNA",
            "Genomic DNA with known introns",
            "Genomic DNA",
            "mRNA"
        ])

        self.seq_type.currentIndexChanged.connect(self.handle_introns)
        self.strand_group = QButtonGroup(self)
        coding_strand = QRadioButton("Coding Strand")
        non_coding_strand = QRadioButton("Non-Coding Strand")
        coding_strand.setChecked(True)
        self.strand_group.addButton(coding_strand)
        self.strand_group.addButton(non_coding_strand)

        self.sequence_input = QTextEdit()
        self.sequence_input.setPlaceholderText("Paste or type your biological sequence...")

        strand_layout = QHBoxLayout()
        strand_layout.addWidget(coding_strand)
        strand_layout.addWidget(non_coding_strand)

        layout.addWidget(QLabel("Sequence Type:"))
        layout.addWidget(self.seq_type)
        layout.addLayout(strand_layout)
        layout.addWidget(QLabel("Input Sequence:"))
        layout.addWidget(self.sequence_input)

        self.setLayout(layout)

    def handle_introns(self):
        if self.seq_type.currentText() == "Genomic DNA with known introns":
            intron_info, ok = QMessageBox.information(self, "Input Introns", "Enter Intron Positions (e.g. 52-75)")
            if ok:
                print("Introns:", intron_info)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secondary Protein Structure Predictor")


        main_layout = QVBoxLayout()
        self.seq_input = Biological_Sequence_Input()

        self.DNA_Graphics = QLabel("DNA Visualizer Placeholder")
        self.Protein_Viewer = QLabel("Protein Viewer Placeholder")
        self.Predict_Button = QPushButton("Predict Secondary Protein Structure")
        self.Result_Viewer = QLabel("Prediction Result Placeholder")

        main_layout.addWidget(self.seq_input)
        main_layout.addWidget(self.DNA_Graphics)
        main_layout.addWidget(self.Protein_Viewer)
        main_layout.addWidget(self.Predict_Button)
        main_layout.addWidget(self.Result_Viewer)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




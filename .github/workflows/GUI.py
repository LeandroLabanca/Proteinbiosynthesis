import sys

from PyQt5.QtWidgets import (
QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
QPushButton, QComboBox, QRadioButton, QButtonGroup, QMessageBox, QScrollArea, QDialog
)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from Proteinbiosynthesis import mRNA_To_DNA, Protein_Translation
from Protein_Structure_Prediction import Protein_Structure_Prediction

Bases = ['A', 'T', 'G', 'C']
Base_Colors = {
    'A': '#A3E635',
    'T': '#F87171',
    'G': '#60A5FA',
    'C': '#FACC15'
}
Base_Pair = {
    'A': 'T',
    'T': 'A',
    'G': 'C',
    'C': 'G'
}

class Biological_Sequence_Input(QWidget):
    Sequence_Updated = pyqtSignal(str, bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ignore_validation = False
        layout = QVBoxLayout()

        self.Seq_Type = QComboBox()
        self.Seq_Type.addItems([
            "Coding Sequence DNA",
            "Genomic DNA with known introns",
            "Genomic DNA",
            "mRNA"
        ])

        self.Seq_Type.currentIndexChanged.connect(self.On_Index_Changed)
        self.Strand_Group = QButtonGroup(self)
        self.Coding_Strand = QRadioButton("Coding Strand")
        self.Non_Coding_Strand = QRadioButton("Non-Coding Strand")
        self.Coding_Strand.setChecked(True)
        self.Strand_Group.addButton(self.Coding_Strand)
        self.Strand_Group.addButton(self.Non_Coding_Strand)

        self.Sequence_Input = QTextEdit()
        self.Sequence_Input.setPlaceholderText("Paste or type your biological sequence...")

        self.Sequence_Input.textChanged.connect(self.Validate_Sequence_Input)
        self._last_valid_text = ""

        Strand_Layout = QHBoxLayout()
        Strand_Layout.addWidget(self.Coding_Strand)
        Strand_Layout.addWidget(self.Non_Coding_Strand)

        layout.addWidget(QLabel("Sequence Type:"))
        layout.addWidget(self.Seq_Type)
        layout.addLayout(Strand_Layout)
        layout.addWidget(QLabel("Input Sequence:"))
        layout.addWidget(self.Sequence_Input)

        self.setLayout(layout)

    def Validate_Sequence_Input(self):
        Seq_Type = self.Seq_Type.currentText()
        Allowed = {'A', 'U', 'G', 'C'} if "mRNA" in Seq_Type else {'A', 'T', 'G', 'C'}

        Current_Text = self.Sequence_Input.toPlainText().upper()
        Valid_Text = ''.join([ch for ch in Current_Text if ch in Allowed])

        if Current_Text != Valid_Text:
            self.Sequence_Input.blockSignals(True)
            self.Sequence_Input.setText(Valid_Text)
            self.Sequence_Input.blockSignals(False)

            QMessageBox.warning(self, "Invalid Character", f"Only the following characters are allowed for {Seq_Type}:\n{', '.join(sorted(Allowed))}")

    def On_Index_Changed(self):
        Current = self.Seq_Type.currentText()
        if Current == "Genomic DNA with known introns":
            self.Coding_Strand.setEnabled(True)
            self.Non_Coding_Strand.setEnabled(True)
            Dialog = Intron_Input(self)
            if Dialog.exec_() == QDialog.Accepted:
                Mode, Data = Dialog.Get_Input_Data()
                Sequence = self.Sequence_Input
                if Mode == "Positions":
                    try:
                        Intron_Ranges = []
                        for part in Data.split(","):
                            Start, End = map(int, part.strip().split("-"))
                            Intron_Ranges.append((Start, End))
                        Intron_Ranges.sort(reverse = True)
                        for Start, End in Intron_Ranges:
                            Start -= 1
                            Sequence = Sequence[:Start]+Sequence[End:]
                    except Exception as e:
                        QMessageBox.warning(self, "Invalid Format", "Use Format like: 42-54")
                        return
                elif Mode == "Sequences":
                    try:
                        Sequence = Sequence.upper().replace('\n', '').replace(' ', '')
                        Introns = [seq.strip().upper().replace('\n', '').replace(' ', '')for seq in Data.replace(',', '\n').split('\n') if seq.strip()]
                        for intron in Introns:
                            if intron in Sequence:
                                Sequence = Sequence.replace(intron, '')
                            else:
                                QMessageBox.information(self, "Intron not found", f"Intron {intron}' was not found.")
                    except Exception as e:
                        QMessageBox.warning(self, "Error")
                self.Sequence_Input.blockSignals(True)
                self.Sequence_Input.setText(Sequence)
                self.Sequence_Input.blockSignals(False)

                Is_Coding_Strand = self.Coding_Strand.isChecked()
                self.Sequence_Updated.emit(Sequence, Is_Coding_Strand)
        if Current == "mRNA":
            self.Coding_Strand.setChecked(True)
            self.Coding_Strand.setEnabled(False)
            self.Non_Coding_Strand.setEnabled(False)
        else:
            self.Coding_Strand.setEnabled(True)
            self.Non_Coding_Strand.setEnabled(True)

#Create a new class for the buttons used in the DNA Visualizer as bases
class Base_Button(QPushButton):
    def __init__(self, Base, Strand, Position, Callback):
        super().__init__(Base)
        #set the strand, position and callback, which gets input as argument
        self.Strand = Strand
        self.Position = Position
        self.Callback = Callback
        #set button size and connect functions
        self.setFixedSize(30,30)
        self.Update_Color()
        self.clicked.connect(self.Cycle_Base)
    def Update_Color(self):
        #set base from string, get corresponding color from palette
        Base = self.text()
        Color = Base_Colors.get(Base, '#E5E7EB')
        Pal = self.palette()
        #set base button color and style of button
        Pal.setColor(QPalette.Button, QColor(Color))
        self.setAutoFillBackground(True)
        self.setPalette(Pal)
        self.setStyleSheet(f"background-color: {Color}; border : 1px solid #333;")
    def Cycle_Base(self):
        #store current amino acid and get index of current amino acid unless not in amino acid list
        Current = self.text()
        I = Bases.index(Current) if Current in Bases else 0
        #cycle to the next base and update its color
        New_Base = Bases[(I+1)%len(Bases)]
        self.setText(New_Base)
        self.Update_Color()
        self.Callback(self.Strand, self.Position, New_Base)

class DNA_Visualizer(QWidget):
    def __init__(self, Sequence_Changed_Callback):
        super().__init__()
        self.layout = QVBoxLayout()
        self.Top_Strand = QHBoxLayout()
        self.Bonds = QHBoxLayout()
        self.Bottom_Strand = QHBoxLayout()

        self.Top_Strand.addWidget(QLabel("5' ->"))
        self.Bonds.addWidget(QLabel("    "))
        self.Bottom_Strand.addWidget(QLabel("3' ->"))

        self.Top_Strand.setSpacing(2)
        self.Bottom_Strand.setSpacing(2)
        self.Bonds.setSpacing(2)

        self.layout.addLayout(self.Top_Strand)
        self.layout.addLayout(self.Bonds)
        self.layout.addLayout(self.Bottom_Strand)

        self.layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        self.Top_Bases = []
        self.Bottom_Bases = []
        self.Is_Coding_Strand = True
        self.Sequence_Changed_Callback = Sequence_Changed_Callback

    def Update_DNA_Strands(self, seq, Is_Coding_Strand = True):
        self.Clear_Layout(self.Top_Strand)
        self.Clear_Layout(self.Bonds)
        self.Clear_Layout(self.Bottom_Strand)

        self.Top_Bases = []
        self.Bottom_Bases = []
        self.Is_Coding_Strand = Is_Coding_Strand

        self.Top_Strand.addWidget(QLabel("5' ->"))
        self.Bonds.addWidget(QLabel("    "))
        self.Bottom_Strand.addWidget(QLabel("3' ->"))

        seq = seq.upper()
        for i, Base in enumerate(seq):
            if Is_Coding_Strand:
                Top_Base = Base
                Bottom_Base = Base_Pair.get(Base, '?')
            else:
                Bottom_Base = Base
                Top_Base = Base_Pair.get(Base, '?')

            Top_Button = Base_Button(Top_Base, 'top', i, self.On_Base_Changed)
            Bottom_Button = Base_Button(Bottom_Base, 'bottom', i, self.On_Base_Changed)

            self.Top_Strand.addWidget(Top_Button)
            self.Bonds.addWidget(QLabel("｜"))
            self.Bottom_Strand.addWidget(Bottom_Button)

            self.Top_Bases.append(Top_Button)
            self.Bottom_Bases.append(Bottom_Button)


    def Clear_Layout(self, layout):
        while layout.count():
            Item = layout.takeAt(0)
            Widget = Item.widget()
            if Widget is not None:
                Widget.setParent(None)
                Widget.deleteLater()

    def On_Base_Changed(self, Strand, Index, New_Base):
        if Strand == 'top':
            Complementary_Base = Base_Pair.get(New_Base, '?')
            self.Bottom_Bases[Index].setText(Complementary_Base)
            self.Bottom_Bases[Index].Update_Color()
        else:
            Complementary_Base = Base_Pair.get(New_Base , '?')
            self.Top_Bases[Index].setText(Complementary_Base)
            self.Top_Bases[Index].Update_Color()

        if self.Is_Coding_Strand:
            New_Seq = ''.join(btn.text() for btn in self.Top_Bases)
        else:
            New_Seq = ''.join(btn.text() for btn in self.Bottom_Bases)

        if self.Sequence_Changed_Callback:
            self.Sequence_Changed_Callback(New_Seq)

class Intron_Input(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Enter Intron information")

        layout = QVBoxLayout()

        self.Position_Radio = QRadioButton("Specify Intron position (e.g. 21-42)")
        self.Sequence_Radio = QRadioButton("Specify Intron sequences (separated by commas/lines)")
        self.Position_Radio.setChecked(True)

        self.Radio_Group = QButtonGroup()
        self.Radio_Group.addButton(self.Position_Radio)
        self.Radio_Group.addButton(self.Sequence_Radio)

        self.Input_Field = QTextEdit()

        self.Ok_Button = QPushButton("OK")
        self.Ok_Button.clicked.connect(self.accept)

        layout.addWidget(self.Position_Radio)
        layout.addWidget(self.Sequence_Radio)
        layout.addWidget(QLabel("Input"))
        layout.addWidget(self.Input_Field)
        layout.addWidget(self.Ok_Button)

        self.setLayout(layout)

    def Get_Input_Data(self):
        return ("Positions" if self.Position_Radio.isChecked() else "Sequences", self.Input_Field.toPlainText().strip())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.Is_Syncing = False
        self.setWindowTitle("Secondary Protein Structure Predictor")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(3840, 2160)

        Main_Layout = QVBoxLayout()
        self.Seq_Input = Biological_Sequence_Input()
        self.Seq_Input.Sequence_Updated.connect(self.Update_Dna_View_With_Sequence)
        self.Dna_Graphics = DNA_Visualizer(self.On_Sequence_Changed_From_Graphics)

        self.Seq_Input.Sequence_Input.textChanged.connect(self.Defer_Update_Dna_View)
        self._deferred_timer = QTimer(self)
        self._deferred_timer.setSingleShot(True)
        self._deferred_timer.timeout.connect(self.Update_Dna_View)

        self.Protein_Viewer = QTextEdit()
        self.Protein_Viewer.setReadOnly(True)
        self.Protein_Viewer.setPlaceholderText("Protein sequence will be displayed here after translation.")
        self.Protein_Viewer.setMinimumHeight(100)
        self.Protein_Viewer.setStyleSheet("font-family: Courier; font-size: 14px;")
        self.Translate_Button = QPushButton("Translate to Protein")
        self.Translate_Button.clicked.connect(self.Run_Translation)

        self.Predict_Button = QPushButton("Predict Protein Secondary Structure")
        self.Predict_Button.clicked.connect(self.Run_Prediction)
        self.Result_Viewer = QTextEdit()
        self.Result_Viewer.setReadOnly(True)
        self.Result_Viewer.setPlaceholderText("Result will be displayed here")
        self.Result_Viewer.setMinimumHeight(100)
        self.Result_Viewer.setStyleSheet("font-family: Courier; font-size: 14px;")

        Main_Layout.addWidget(self.Seq_Input)
        Scroll = QScrollArea()
        Scroll.setWidgetResizable(True)
        Scroll.setWidget(self.Dna_Graphics)
        Scroll.setMinimumHeight(120)
        Scroll.setWidgetResizable(False)

        Main_Layout.addWidget(QLabel("DNA Strand Visualizer:"))
        Main_Layout.addWidget(Scroll)
        Main_Layout.addWidget(self.Protein_Viewer)
        Main_Layout.addWidget(self.Translate_Button)
        Main_Layout.addWidget(self.Predict_Button)
        Main_Layout.addWidget(self.Result_Viewer)


        Container = QWidget()
        Container.setLayout(Main_Layout)
        self.setCentralWidget(Container)

    def Update_Dna_View(self):
        if self.Is_Syncing:
            return
        self.Is_Syncing = True

        Seq_Type = self.Seq_Input.Seq_Type.currentText()
        Sequence = self.Seq_Input.Sequence_Input.toPlainText().upper()
        Is_Coding_Strand = self.Seq_Input.Strand_Group.checkedButton().text() == "Coding Strand"
        if not Sequence.strip():
            self.Dna_Graphics.Update_DNA_Strands("", Is_Coding_Strand)
            self.Is_Syncing = False
            return


        Visual_Seq = Sequence
        if Seq_Type == "mRNA":
            Visual_Seq = mRNA_To_DNA(Sequence)
            if not Visual_Seq:
                QMessageBox.warning(self, "Back-transcription failed")
                self.Is_Syncing = False
                return

            self.Seq_Input.Sequence_Input.blockSignals(True)
            self.Seq_Input.Sequence_Input.setText(Sequence)
            self.Seq_Input.Sequence_Input.blockSignals(False)

            self.Seq_Input.Coding_Strand.setChecked(True)
            Is_Coding_Strand = True

        self.Dna_Graphics.Update_DNA_Strands(Visual_Seq, Is_Coding_Strand)

        self.Is_Syncing = False

    def Defer_Update_Dna_View(self):
        self._deferred_timer.start(10)

    def On_Sequence_Changed_From_Graphics(self, New_Sequence):
        self.Is_Syncing = True
        Seq_Type = self.Seq_Input.Seq_Type.currentText()
        if Seq_Type == "mRNA":
            mRNA_Sequence = New_Sequence.replace('T', 'U')
            self.Seq_Input.Sequence_Input.setPlainText(mRNA_Sequence)

            Cursor = self.Seq_Input.Sequence_Input.textCursor()
            Cursor.movePosition(Cursor.End)
            self.Seq_Input.Sequence_Input.setTextCursor(Cursor)
        else:
            self.Seq_Input.Sequence_Input.setPlainText(New_Sequence)

        self.Is_Syncing = False

    def Run_Translation(self):
        Sequence = self.Seq_Input.Sequence_Input.toPlainText().upper().replace('\n', '').replace(' ', '')
        Seq_Type = self.Seq_Input.Seq_Type.currentText()
        if Sequence=="":
            QMessageBox.warning(self, "Please enter a sequence to translate")
            return
        else:
            Is_mRNA = Seq_Type == "mRNA"
            Is_Non_Coding_strand = self.Seq_Input.Strand_Group.checkedButton().text() == "Non-Coding Strand"
            Protein = Protein_Translation(Sequence, Is_mRNA, Is_Non_Coding_strand)
            self.Protein_Viewer.setText(f"Protein:\n{Protein}")

    def Update_Dna_View_With_Sequence(self, Sequence, Is_Coding_Strand):
        if self.Is_Syncing:
            return
        self.Is_Syncing = True
        self.Seq_Input.Sequence_Input.blockSignals(True)
        self.Seq_Input.Sequence_Input.setPlainText(Sequence)
        self.Seq_Input.Sequence_Input.blockSignals(False)
        self.Dna_Graphics.Update_DNA_Strands(Sequence, Is_Coding_Strand)
        self.Is_Syncing = False

    def Run_Prediction(self):
        Protein_Seq = self.Protein_Viewer.toPlainText().replace("Protein:\n", "").strip()
        print(Protein_Seq)
        if not Protein_Seq:
            QMessageBox.warning(self, "Please enter a sequence to predict")
            return

        try:
            Amino_Acid_seq, Prediction, Counts = Protein_Structure_Prediction(Protein_Seq)
        except Exception as e:
            QMessageBox.warning(self, "Prediction error", str(e))
            return
        Summary = " ".join([f"{label}:{Counts[label]}" for label in sorted(Counts.keys())])
        self.Result_Viewer.blockSignals(True)
        self.Result_Viewer.setPlainText(
            f"Predicted Structure:\n{Prediction}\n\n"
            f"Summary:\n{Summary}"
        )
        self.Result_Viewer.blockSignals(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




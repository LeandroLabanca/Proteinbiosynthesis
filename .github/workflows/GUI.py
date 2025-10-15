import sys

from PyQt5.QtWidgets import (
QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
QPushButton, QComboBox, QRadioButton, QButtonGroup, QMessageBox, QScrollArea, QDialog
)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from Proteinbiosynthesis import mRNA_To_DNA, Protein_Translation
from Protein_Structure_Prediction import Protein_Structure_Prediction

#define bases, for back-transcription inside of GUI file
#not having to import Biopython
Bases = ['A', 'T', 'G', 'C']
#define colors of the buttons
#asked OpenAIs GPT-5 for hex codes for colors red, green, blue, yellow
Base_Colors = {
    'A': '#A3E635',
    'T': '#F87171',
    'G': '#60A5FA',
    'C': '#FACC15'
}
#define complementary bases
Base_Pair = {
    'A': 'T',
    'T': 'A',
    'G': 'C',
    'C': 'G'
}

#define first class for input field
class Biological_Sequence_Input(QWidget):
    Sequence_Updated = pyqtSignal(str, bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ignore_validation = False
        #setting vertical layout
        layout = QVBoxLayout()

        #create dropdown list to choose input types
        self.Seq_Type = QComboBox()
        self.Seq_Type.addItems([
            "Coding Sequence DNA",
            "Genomic DNA with known introns",
            "Genomic DNA",
            "mRNA"
        ])

        #create buttons to choose between coding and non-coding strand
        self.Seq_Type.currentIndexChanged.connect(self.On_Index_Changed)
        self.Strand_Group = QButtonGroup(self)
        self.Coding_Strand = QRadioButton("Coding Strand")
        self.Non_Coding_Strand = QRadioButton("Non-Coding Strand")
        self.Coding_Strand.setChecked(True)
        self.Strand_Group.addButton(self.Coding_Strand)
        self.Strand_Group.addButton(self.Non_Coding_Strand)

        #create input field, set placeholder text
        self.Sequence_Input = QTextEdit()
        self.Sequence_Input.setPlaceholderText("Paste or type your biological sequence...")

        #connect input validation function
        self.Sequence_Input.textChanged.connect(self.Validate_Sequence_Input)
        self._last_valid_text = ""

        Strand_Layout = QHBoxLayout()
        Strand_Layout.addWidget(self.Coding_Strand)
        Strand_Layout.addWidget(self.Non_Coding_Strand)

        #adding widgets to layout
        layout.addWidget(QLabel("Sequence Type:"))
        layout.addWidget(self.Seq_Type)
        layout.addLayout(Strand_Layout)
        layout.addWidget(QLabel("Input Sequence:"))
        layout.addWidget(self.Sequence_Input)

        #setting layout
        self.setLayout(layout)

    #create input validation function
    #remove invalid characters, depending on chosen sequence type.
    def Validate_Sequence_Input(self):
        Seq_Type = self.Seq_Type.currentText()
        Allowed = {'A', 'U', 'G', 'C'} if "mRNA" in Seq_Type else {'A', 'T', 'G', 'C'}

        Current_Text = self.Sequence_Input.toPlainText().upper()
        Valid_Text = ''.join([ch for ch in Current_Text if ch in Allowed])

        #block signal statements before setting text
        #ensure no infinite recursive loop with the DNA visualizer appears
        if Current_Text != Valid_Text:
            self.Sequence_Input.blockSignals(True)
            self.Sequence_Input.setText(Valid_Text)
            self.Sequence_Input.blockSignals(False)

            #warning message to the user, if not allowed characters were used
            QMessageBox.warning(self, "Invalid Character", f"Only the following characters are allowed for {Seq_Type}:\n{', '.join(sorted(Allowed))}")

    #function gets called if the sequence type in the dropdown list is changed
    #handles intron removal modes and strand enabling/disabling
    def On_Index_Changed(self):
        Current = self.Seq_Type.currentText()
        #removes introns after mode has been selected in popup
        #intron ranges or sequences selection is checked
        if Current == "Genomic DNA with known introns":
            self.Coding_Strand.setEnabled(True)
            self.Non_Coding_Strand.setEnabled(True)
            Dialog = Intron_Input(self)
            if Dialog.exec_() == QDialog.Accepted:
                Mode, Data = Dialog.Get_Input_Data()
                Sequence = self.Sequence_Input
                #mode for input ranges
                #user specifies index range, where the intron lies and that range is then removed
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
                #mode for specific intron sequences to be removed
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
        #disable non-coding strand option, because mRNA is always the same as the coding strand
        # with Us instead of Ts
        if Current == "mRNA":
            self.Coding_Strand.setChecked(True)
            self.Coding_Strand.setEnabled(False)
            self.Non_Coding_Strand.setEnabled(False)
        else:
            self.Coding_Strand.setEnabled(True)
            self.Non_Coding_Strand.setEnabled(True)

#create a new class for the buttons used in the DNA Visualizer as bases
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

#DNA visualizer class is defined
class DNA_Visualizer(QWidget):
    def __init__(self, Sequence_Changed_Callback):
        super().__init__()
        #general  layout is set and layouts for the different items, the top strand, the bonds in between and the bottom strand are added
        self.layout = QVBoxLayout()
        self.Top_Strand = QHBoxLayout()
        self.Bonds = QHBoxLayout()
        self.Bottom_Strand = QHBoxLayout()

        #strands are labelled and bonds recieve whitespaces in labelling for equal offset
        self.Top_Strand.addWidget(QLabel("5' ->"))
        self.Bonds.addWidget(QLabel("    "))
        self.Bottom_Strand.addWidget(QLabel("3' ->"))

        #space in between strands and bonds is set
        self.Top_Strand.setSpacing(2)
        self.Bottom_Strand.setSpacing(2)
        self.Bonds.setSpacing(2)

        #created widgets are added to the layout
        self.layout.addLayout(self.Top_Strand)
        self.layout.addLayout(self.Bonds)
        self.layout.addLayout(self.Bottom_Strand)

        #setting a size layout, to ensure, that no complications happen
        self.layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        #empty lists for the bases are created
        self.Top_Bases = []
        self.Bottom_Bases = []
        self.Is_Coding_Strand = True
        self.Sequence_Changed_Callback = Sequence_Changed_Callback

    #function to update the strands is created
    def Update_DNA_Strands(self, seq, Is_Coding_Strand = True):
        #layouts are cleared
        self.Clear_Layout(self.Top_Strand)
        self.Clear_Layout(self.Bonds)
        self.Clear_Layout(self.Bottom_Strand)

        #empty list for top and bottom bases defined
        self.Top_Bases = []
        self.Bottom_Bases = []
        self.Is_Coding_Strand = Is_Coding_Strand

        #strands are labelled as previously (has to be done again after the Clear_Layout function)
        self.Top_Strand.addWidget(QLabel("5' ->"))
        self.Bonds.addWidget(QLabel("    "))
        self.Bottom_Strand.addWidget(QLabel("3' ->"))

        #input sequence is set to uppercase and the base and complementary one are defined
        seq = seq.upper()
        for i, Base in enumerate(seq):
            if Is_Coding_Strand:
                Top_Base = Base
                Bottom_Base = Base_Pair.get(Base, '?')
            else:
                Bottom_Base = Base
                Top_Base = Base_Pair.get(Base, '?')

            #the base and complimentary base are set to the respective button, depending on if coding strand or non-coding strand was selected
            Top_Button = Base_Button(Top_Base, 'top', i, self.On_Base_Changed)
            Bottom_Button = Base_Button(Bottom_Base, 'bottom', i, self.On_Base_Changed)

            #button is added to strand and bond is added
            self.Top_Strand.addWidget(Top_Button)
            self.Bonds.addWidget(QLabel("｜"))
            self.Bottom_Strand.addWidget(Bottom_Button)

            #button is appended to the base list
            self.Top_Bases.append(Top_Button)
            self.Bottom_Bases.append(Bottom_Button)

    #clear function is defined, which completely clears the layout
    def Clear_Layout(self, layout):
        while layout.count():
            Item = layout.takeAt(0)
            Widget = Item.widget()
            if Widget is not None:
                Widget.setParent(None)
                Widget.deleteLater()

    #function for button cycling is defined
    def On_Base_Changed(self, Strand, Index, New_Base):
        #get the complementary base for the not input strand
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

#define class for intron removal
class Intron_Input(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Enter Intron information")

        layout = QVBoxLayout()
        #add buttons to choose between removal modes
        self.Position_Radio = QRadioButton("Specify Intron position (e.g. 21-42)")
        self.Sequence_Radio = QRadioButton("Specify Intron sequences (separated by commas/lines)")
        self.Position_Radio.setChecked(True)

        #add buttons to button group
        self.Radio_Group = QButtonGroup()
        self.Radio_Group.addButton(self.Position_Radio)
        self.Radio_Group.addButton(self.Sequence_Radio)

        #add input field for introns
        self.Input_Field = QTextEdit()

        #add button to execute
        self.Ok_Button = QPushButton("OK")
        self.Ok_Button.clicked.connect(self.accept)

        #adding buttons and labels to layout
        layout.addWidget(self.Position_Radio)
        layout.addWidget(self.Sequence_Radio)
        layout.addWidget(QLabel("Input"))
        layout.addWidget(self.Input_Field)
        layout.addWidget(self.Ok_Button)

        self.setLayout(layout)

    #default value is positional removal through index range specification
    #for sequence removal users have to click the sequence option
    def Get_Input_Data(self):
        return ("Positions" if self.Position_Radio.isChecked() else "Sequences", self.Input_Field.toPlainText().strip())

#define the MainWindow, which calls all other classes
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.Is_Syncing = False
        #setting title and window size limitations
        self.setWindowTitle("Secondary Protein Structure Predictor")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(3840, 2160)

        #creating layout and adding previously defined classes
        Main_Layout = QVBoxLayout()
        self.Seq_Input = Biological_Sequence_Input()
        self.Seq_Input.Sequence_Updated.connect(self.Update_Dna_View_With_Sequence)
        self.Dna_Graphics = DNA_Visualizer(self.On_Sequence_Changed_From_Graphics)

        #adds a timer for 10 ms delay after a user types, because else changes won't be made to the DNA visualizer because of sequence of operations
        self.Seq_Input.Sequence_Input.textChanged.connect(self.Defer_Update_Dna_View)
        self._deferred_timer = QTimer(self)
        self._deferred_timer.setSingleShot(True)
        self._deferred_timer.timeout.connect(self.Update_Dna_View)

        #create protein field and set text variables
        self.Protein_Viewer = QTextEdit()
        self.Protein_Viewer.setReadOnly(True)
        self.Protein_Viewer.setPlaceholderText("Protein sequence will be displayed here after translation.")
        self.Protein_Viewer.setMinimumHeight(100)
        self.Protein_Viewer.setStyleSheet("font-family: Courier; font-size: 14px;")
        self.Translate_Button = QPushButton("Translate to Protein")
        self.Translate_Button.clicked.connect(self.Run_Translation)

        #create secondary structure prediction field and set text variables
        self.Predict_Button = QPushButton("Predict Protein Secondary Structure")
        self.Predict_Button.clicked.connect(self.Run_Prediction)
        self.Result_Viewer = QTextEdit()
        self.Result_Viewer.setReadOnly(True)
        self.Result_Viewer.setPlaceholderText("Result will be displayed here")
        self.Result_Viewer.setMinimumHeight(100)
        self.Result_Viewer.setStyleSheet("font-family: Courier; font-size: 14px;")

        #add input field widget to layout and create a scrollable area for the DNA visualizer
        Main_Layout.addWidget(self.Seq_Input)
        Scroll = QScrollArea()
        Scroll.setWidgetResizable(True)
        Scroll.setWidget(self.Dna_Graphics)
        Scroll.setMinimumHeight(120)
        Scroll.setWidgetResizable(False)

        #add the different widgets to the layout
        Main_Layout.addWidget(QLabel("DNA Strand Visualizer:"))
        Main_Layout.addWidget(Scroll)
        Main_Layout.addWidget(self.Protein_Viewer)
        Main_Layout.addWidget(self.Translate_Button)
        Main_Layout.addWidget(self.Predict_Button)
        Main_Layout.addWidget(self.Result_Viewer)

        #setting all widgets to the layout in the application
        Container = QWidget()
        Container.setLayout(Main_Layout)
        self.setCentralWidget(Container)

    #create flag against recursive infinite loop
    def Update_Dna_View(self):
        if self.Is_Syncing:
            return
        self.Is_Syncing = True

        #set sequence type, sequence and strand type according to users selection/input
        Seq_Type = self.Seq_Input.Seq_Type.currentText()
        Sequence = self.Seq_Input.Sequence_Input.toPlainText().upper()
        Is_Coding_Strand = self.Seq_Input.Strand_Group.checkedButton().text() == "Coding Strand"
        if not Sequence.strip():
            self.Dna_Graphics.Update_DNA_Strands("", Is_Coding_Strand)
            self.Is_Syncing = False
            return

        #create display sequence and display it
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

        #update DNA visualizer with new values
        self.Dna_Graphics.Update_DNA_Strands(Visual_Seq, Is_Coding_Strand)

        self.Is_Syncing = False

    #10 ms delay for DNA visualizer updates
    def Defer_Update_Dna_View(self):
        self._deferred_timer.start(10)

    #replace Ts with Us after changing to mRNA
    def On_Sequence_Changed_From_Graphics(self, New_Sequence):
        self.Is_Syncing = True
        Seq_Type = self.Seq_Input.Seq_Type.currentText()
        if Seq_Type == "mRNA":
            mRNA_Sequence = New_Sequence.replace('T', 'U')
            self.Seq_Input.Sequence_Input.setPlainText(mRNA_Sequence)

            #set cursor to the end of the string, but still does not work for some reason
            #not sure why and is to be improved for possible future versions
            Cursor = self.Seq_Input.Sequence_Input.textCursor()
            Cursor.movePosition(Cursor.End)
            self.Seq_Input.Sequence_Input.setTextCursor(Cursor)
        else:
            self.Seq_Input.Sequence_Input.setPlainText(New_Sequence)

        self.Is_Syncing = False

    #call the translation function and clean input before
    def Run_Translation(self):
        Sequence = self.Seq_Input.Sequence_Input.toPlainText().upper().replace('\n', '').replace(' ', '')
        Seq_Type = self.Seq_Input.Seq_Type.currentText()
        #warn if an empty sequence was input and stop execution for error prevention
        if Sequence=="":
            QMessageBox.warning(self, "Please enter a sequence to translate")
            return
        #translate the input and create variable for input into Protein_Translation function, to check if input type is mRNA for back transcription
        else:
            Is_mRNA = Seq_Type == "mRNA"
            Is_Non_Coding_strand = self.Seq_Input.Strand_Group.checkedButton().text() == "Non-Coding Strand"
            Protein = Protein_Translation(Sequence, Is_mRNA, Is_Non_Coding_strand)
            self.Protein_Viewer.setText(f"Protein:\n{Protein}")

    #update DNA visualizer with new sequence
    def Update_Dna_View_With_Sequence(self, Sequence, Is_Coding_Strand):
        if self.Is_Syncing:
            return
        self.Is_Syncing = True
        self.Seq_Input.Sequence_Input.blockSignals(True)
        self.Seq_Input.Sequence_Input.setPlainText(Sequence)
        self.Seq_Input.Sequence_Input.blockSignals(False)
        self.Dna_Graphics.Update_DNA_Strands(Sequence, Is_Coding_Strand)
        self.Is_Syncing = False

    #run the machine learning model indirectly, through calling the Run_Prediction function imported from Protein_Structure_Prediction
    def Run_Prediction(self):
        #clean input sequence to ensure no errors
        Protein_Seq = self.Protein_Viewer.toPlainText().replace("Protein:\n", "").strip()
        print(Protein_Seq)
        #error message if Translation was not done yet, so the model would have no input to predict
        if not Protein_Seq:
            QMessageBox.warning(self, "Please enter a sequence to predict")
            return

        #attempt the prediction and get the protein, the per residue prediction string and the count for each label
        #counts are the amount of times a certain secondary structure appears in the prediction
        try:
            Amino_Acid_seq, Prediction, Counts = Protein_Structure_Prediction(Protein_Seq)
        #warn if a prediction error appears
        except Exception as e:
            QMessageBox.warning(self, "Prediction error", str(e))
            return

        #create collection of prediction string and counts, to display both inside of prediction viewer field
        Summary = " ".join([f"{label}:{Counts[label]}" for label in sorted(Counts.keys())])
        self.Result_Viewer.blockSignals(True)
        self.Result_Viewer.setPlainText(
            f"Predicted Structure:\n{Prediction}\n\n"
            f"Summary:\n{Summary}"
        )
        self.Result_Viewer.blockSignals(False)

#standard PyQt5 startup sequence with exit if user closes it
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




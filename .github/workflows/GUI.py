import sys
from operator import index
from PyQt5.QtWidgets import (
QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QComboBox, QRadioButton, QButtonGroup, QMessageBox, QScrollArea, QFrame, QInputDialog, QDialog
)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from proteinbiosynthesis import mRNA_to_DNA, Protein_Translation

Bases = ['A', 'T', 'G', 'C']
Base_Colors = {
    'A': '#A3E635',
    'T': '#F87171',
    'G': '#60A5FA',
    'C': '#FACC15'
}
BASE_PAIR = {
    'A': 'T',
    'T': 'A',
    'G': 'C',
    'C': 'G'
}

class Biological_Sequence_Input(QWidget):
    sequence_updated = pyqtSignal(str, bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ignore_validation = False
        layout = QVBoxLayout()

        self.seq_type = QComboBox()
        self.seq_type.addItems([
            "Coding Sequence DNA",
            "Genomic DNA with known introns",
            "Genomic DNA",
            "mRNA"
        ])

        self.seq_type.currentIndexChanged.connect(self.On_Index_Changed)
        self.strand_group = QButtonGroup(self)
        self.coding_strand = QRadioButton("Coding Strand")
        self.non_coding_strand = QRadioButton("Non-Coding Strand")
        self.coding_strand.setChecked(True)
        self.strand_group.addButton(self.coding_strand)
        self.strand_group.addButton(self.non_coding_strand)

        self.sequence_input = QTextEdit()
        self.sequence_input.setPlaceholderText("Paste or type your biological sequence...")

        self.sequence_input.textChanged.connect(self.validate_sequence_input)
        self._last_valid_text = ""

        strand_layout = QHBoxLayout()
        strand_layout.addWidget(self.coding_strand)
        strand_layout.addWidget(self.non_coding_strand)

        layout.addWidget(QLabel("Sequence Type:"))
        layout.addWidget(self.seq_type)
        layout.addLayout(strand_layout)
        layout.addWidget(QLabel("Input Sequence:"))
        layout.addWidget(self.sequence_input)

        self.setLayout(layout)

    def validate_sequence_input(self):
        seq_type = self.seq_type.currentText()
        allowed = {'A', 'U', 'G', 'C'} if "mRNA" in seq_type else {'A', 'T', 'G', 'C'}

        current_text = self.sequence_input.toPlainText().upper()
        valid_text = ''.join([ch for ch in current_text if ch in allowed])

        if current_text != valid_text:
            self.sequence_input.blockSignals(True)
            self.sequence_input.setText(valid_text)
            self.sequence_input.blockSignals(False)

            QMessageBox.warning(self, "Invalid Character", f"Only the following characters are allowed for {seq_type}:\n{', '.join(sorted(allowed))}")

    def On_Index_Changed(self):
        current = self.seq_type.currentText()
        if current == "Genomic DNA with known introns":
            self.coding_strand.setEnabled(True)
            self.non_coding_strand.setEnabled(True)
            dialog = Intron_Input(self)
            if dialog.exec_() == QDialog.Accepted:
                mode, data = dialog.Get_Input_Data()
                sequence = self.sequence_input.toPlainText().upper()
                if mode == "Positions":
                    try:
                        Intron_Ranges = []
                        for part in data.split(","):
                            start, end = map(int, part.strip().split("-"))
                            Intron_Ranges.append((start, end))
                        Intron_Ranges.sort(reverse = True)
                        for start, end in Intron_Ranges:
                            start -= 1
                            sequence = sequence[:start]+sequence[end:]
                    except Exception as e:
                        QMessageBox.warning(self, "Invalid Format", "Use Format like: 42-54")
                        return
                elif mode == "Sequences":
                    try:
                        sequence = sequence.upper().replace('\n', '').replace(' ', '')
                        introns = [seq.strip().upper().replace('\n', '').replace(' ', '')for seq in data.replace(',', '\n').split('\n') if seq.strip()]
                        for intron in introns:
                            if intron in sequence:
                                sequence = sequence.replace(intron, '')
                            else:
                                QMessageBox.information(self, "Intron not found", f"Intron {intron}' was not found.")
                    except Exception as e:
                        QMessageBox.warning(self, "Error")
                self.sequence_input.blockSignals(True)
                self.sequence_input.setText(sequence)
                self.sequence_input.blockSignals(False)

                is_coding_strand = self.coding_strand.isChecked()
                self.sequence_updated.emit(sequence, is_coding_strand)
        if current == "mRNA":
            self.coding_strand.setChecked(True)
            self.coding_strand.setEnabled(False)
            self.non_coding_strand.setEnabled(False)
        else:
            self.coding_strand.setEnabled(True)
            self.non_coding_strand.setEnabled(True)

class Base_Button(QPushButton):
    def __init__(self, base, strand, position, callback):
        super().__init__(base)
        self.strand = strand
        self.position = position
        self.callback = callback
        self.setFixedSize(30,30)
        self.update_color()
        self.clicked.connect(self.cycle_base)

    def update_color(self):
        base = self.text()
        color = Base_Colors.get(base, '#E5E7EB')
        pal = self.palette()
        pal.setColor(QPalette.Button, QColor(color))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        self.setStyleSheet(f"background-color: {color}; border : 1px solid #333;")

    def cycle_base(self):
        current = self.text()
        i = Bases.index(current) if current in Bases else 0
        new_base = Bases[(i+1)%len(Bases)]
        self.setText(new_base)
        self.update_color()
        self.callback(self.strand, self.position, new_base)

class DNA_Visualizer(QWidget):
    def __init__(self, sequence_changed_callback):
        super().__init__()
        self.layout = QVBoxLayout()
        self.top_strand = QHBoxLayout()
        self.bonds = QHBoxLayout()
        self.bottom_strand = QHBoxLayout()

        self.top_strand.addWidget(QLabel("5' ->"))
        self.bonds.addWidget(QLabel("    "))
        self.bottom_strand.addWidget(QLabel("3' ->"))

        self.top_strand.setSpacing(2)
        self.bottom_strand.setSpacing(2)
        self.bonds.setSpacing(2)

        self.layout.addLayout(self.top_strand)
        self.layout.addLayout(self.bonds)
        self.layout.addLayout(self.bottom_strand)

        self.layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        self.top_bases = []
        self.bottom_bases = []
        self.is_coding_strand = True
        self.sequence_changed_callback = sequence_changed_callback

    def Update_DNA_Strands(self, seq, is_coding_strand = True):
        self._clear_layout(self.top_strand)
        self._clear_layout(self.bonds)
        self._clear_layout(self.bottom_strand)

        self.top_bases = []
        self.bottom_bases = []
        self.is_coding_strand = is_coding_strand

        self.top_strand.addWidget(QLabel("5' ->"))
        self.bonds.addWidget(QLabel("    "))
        self.bottom_strand.addWidget(QLabel("3' ->"))

        seq = seq.upper()
        for i, base in enumerate(seq):
            if is_coding_strand:
                top_base = base
                bottom_base = BASE_PAIR.get(base, '?')
            else:
                bottom_base = base
                top_base = BASE_PAIR.get(base, '?')

            top_button = Base_Button(top_base, 'top', i, self.on_base_changed)
            bottom_button = Base_Button(bottom_base, 'bottom', i, self.on_base_changed)

            self.top_strand.addWidget(top_button)
            self.bonds.addWidget(QLabel("｜"))
            self.bottom_strand.addWidget(bottom_button)

            self.top_bases.append(top_button)
            self.bottom_bases.append(bottom_button)


    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def on_base_changed(self, strand, index, new_base):
        if strand == 'top':
            comp_base = BASE_PAIR.get(new_base, '?')
            self.bottom_bases[index].setText(comp_base)
            self.bottom_bases[index].update_color()
        else:
            comp_base = BASE_PAIR.get(new_base , '?')
            self.top_bases[index].setText(comp_base)
            self.top_bases[index].update_color()

        if self.is_coding_strand:
            new_seq = ''.join(btn.text() for btn in self.top_bases)
        else:
            new_seq = ''.join(btn.text() for btn in self.bottom_bases)

        if self.sequence_changed_callback:
            self.sequence_changed_callback(new_seq)

class Intron_Input(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Enter Intron information")

        layout = QVBoxLayout()

        self.position_radio = QRadioButton("Specify Intron position (e.g. 21-42)")
        self.sequence_radio = QRadioButton("Specify Intron sequences (separated by commas/lines)")
        self.position_radio.setChecked(True)

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.position_radio)
        self.radio_group.addButton(self.sequence_radio)

        self.input_field = QTextEdit()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout.addWidget(self.position_radio)
        layout.addWidget(self.sequence_radio)
        layout.addWidget(QLabel("Input"))
        layout.addWidget(self.input_field)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def Get_Input_Data(self):
        return ("Positions" if self.position_radio.isChecked() else "Sequences", self.input_field.toPlainText().strip())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_syncing = False
        self.setWindowTitle("Secondary Protein Structure Predictor")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(3840, 2160)

        main_layout = QVBoxLayout()
        self.seq_input = Biological_Sequence_Input()
        self.seq_input.sequence_updated.connect(self.update_dna_view_with_sequence)
        self.dna_graphics = DNA_Visualizer(self.on_sequence_changed_from_graphics)

        self.seq_input.sequence_input.textChanged.connect(self.defer_update_dna_view)
        self._deferred_timer = QTimer(self)
        self._deferred_timer.setSingleShot(True)
        self._deferred_timer.timeout.connect(self.update_dna_view)

        self.Protein_Viewer = QLabel("Protein Viewer Placeholder")
        self.Translate_Button = QPushButton("Translate to Protein")
        self.Translate_Button.clicked.connect(self.Run_Translation)
        self.Predict_Button = QPushButton("Predict Secondary Protein Structure")
        self.Result_Viewer = QLabel("Prediction Result Placeholder")

        main_layout.addWidget(self.seq_input)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.dna_graphics)
        scroll.setMinimumHeight(120)
        scroll.setWidgetResizable(False)

        main_layout.addWidget(QLabel("DNA Strand Visualizer:"))
        main_layout.addWidget(scroll)
        main_layout.addWidget(self.Protein_Viewer)
        main_layout.addWidget(self.Translate_Button)
        main_layout.addWidget(self.Predict_Button)
        main_layout.addWidget(self.Result_Viewer)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def update_dna_view(self):
        if self.is_syncing:
            return
        self.is_syncing = True

        seq_type = self.seq_input.seq_type.currentText()
        sequence = self.seq_input.sequence_input.toPlainText().upper()
        is_coding_strand = self.seq_input.strand_group.checkedButton().text() == "Coding Strand"
        if not sequence.strip():
            self.dna_graphics.Update_DNA_Strands("", is_coding_strand)
            self.is_syncing = False
            return


        visual_seq = sequence
        if seq_type == "mRNA":
            visual_seq = mRNA_to_DNA(sequence)
            if not visual_seq:
                QMessageBox.warning(self, "Back-transcription failed")
                self.is_syncing = False
                return

            self.seq_input.sequence_input.blockSignals(True)
            self.seq_input.sequence_input.setText(sequence)
            self.seq_input.sequence_input.blockSignals(False)

            self.seq_input.coding_strand.setChecked(True)
            is_coding_strand = True

        self.dna_graphics.Update_DNA_Strands(visual_seq, is_coding_strand)

        self.is_syncing = False

    def defer_update_dna_view(self):
        self._deferred_timer.start(10)

    def on_sequence_changed_from_graphics(self, new_sequence):
        self.is_syncing = True
        seq_type = self.seq_input.seq_type.currentText()
        if seq_type == "mRNA":
            mrna_sequence = new_sequence.replace('T', 'U')
            self.seq_input.sequence_input.setPlainText(mrna_sequence)

            cursor = self.seq_input.sequence_input.textCursor()
            cursor.movePosition(cursor.End)
            self.seq_input.sequence_input.setTextCursor(cursor)
        else:
            self.seq_input.sequence_input.setPlainText(new_sequence)

        self.is_syncing = False

    def Run_Translation(self):
        sequence = self.seq_input.sequence_input.toPlainText().upper().replace('\n', '').replace(' ', '')
        seq_type = self.seq_input.seq_type.currentText()
        if not sequence:
            QMessageBox.warning(self, "Please enter a sequence to translate")
            return
        else:
            is_mRNA = seq_type == "mRNA"
            is_NonCoding_strand = self.seq_input.strand_group.checkedButton().text() == "Non-Coding Strand"
            protein = Protein_Translation(sequence, is_mRNA)
            formatted = '\n'.join([protein[i:i+60]for i in range(0, len(protein),60)])
            self.Protein_Viewer.setText(f"Protein:\n{formatted}")

    def update_dna_view_with_sequence(self, sequence, is_coding_strand):
        if self.is_syncing:
            return
        self.is_syncing = True
        self.seq_input.sequence_input.blockSignals(True)
        self.seq_input.sequence_input.setPlainText(sequence)
        self.seq_input.sequence_input.blockSignals(False)
        self.dna_graphics.Update_DNA_Strands(sequence, is_coding_strand)
        self.is_syncing = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




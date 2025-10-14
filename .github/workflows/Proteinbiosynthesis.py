from Bio.Seq import Seq

def mRNA_To_DNA(mRNA_Sequence):
    try:
        return str(Seq(mRNA_Sequence.upper()).back_transcribe())
    except Exception as e:
        print(f"Error during back-transcription: {e}")
        return ""

def Protein_Translation(Nucleotide_Sequence, Is_mRNA, Is_Non_Coding_Strand):
    seq = Seq(Nucleotide_Sequence.upper().replace("\n", "").replace(" ", ""))
    if Is_Non_Coding_Strand:
        seq = seq.reverse_complement()
    elif Is_mRNA:
        seq = seq.back_transcribe()
    protein = seq.translate(stop_symbol = "")
    return str(protein)




def Intron_Search_Database():#later
    pass

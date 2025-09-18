from Bio.Seq import Seq






def mRNA_to_DNA(mRNA_sequence: str)->str:
    try:
        return str(Seq(mRNA_sequence.upper()).back_transcribe())
    except Exception as e:
        print(f"Error during back-transcription: {e}")
        return ""

def Protein_Translation(nucleotide_sequence: str, is_mRNA: bool = False, is_NonCoding_Strand: bool = False)->str:
    seq = Seq(nucleotide_sequence.upper().replace("\n", "").replace(" ", ""))
    if is_NonCoding_Strand:
        pass
    elif is_mRNA:
        seq = seq.back_transcribe()
    protein = seq.translate(stop_symbol = "")
    return str(protein)




def intron_search_database():#later
    pass

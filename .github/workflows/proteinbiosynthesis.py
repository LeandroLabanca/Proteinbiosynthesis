from Bio.Seq import Seq

def read():
    path = "C:/Users/leand/Downloads/"
    filename = "1a80.txt"
    file = open(path  + filename, "r")
    global gene
    gene = file.read()
    #removing newlines \n and removing carriage return \r for formatting
    gene = gene.replace ("\n", "").replace("\r", "")


#def non_coding_strand_to_coding_strand(): #helper function, to change from non coding to coding strand etc.
    global coding_strand
    global non_coding_strand
    non_coding_strand = gene
    coding_strand = ""
    for base in gene:
        if base == "A":
            coding_strand += "T"
        elif base == "C":
            coding_strand += "G"
        elif base == "G":
            coding_strand += "C"
        elif base == "T":
            coding_strand += "A"

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

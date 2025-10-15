#import Biopython Sequence functions
from Bio.Seq import Seq

#define back transcription, used for the creation of the base strand in the DNA Visualizer widget
def mRNA_To_DNA(mRNA_Sequence):
    try:
        #convert mRNA back into its corresponding DNA sequence
        #used for the DNA visualizers DNA strands
        return str(Seq(mRNA_Sequence.upper()).back_transcribe())
    #error message in console if back-transcription gets an error
    except Exception as e:
        print(f"Error during back-transcription: {e}")
        return ""

#define protein translation, differentiating the different sequence input types
def Protein_Translation(Nucleotide_Sequence, Is_mRNA, Is_Non_Coding_Strand):
    #additional sequence cleanup, because others did not work before, because else Biopythons .translate() function wont work
    seq = Seq(Nucleotide_Sequence.upper().replace("\n", "").replace(" ", ""))
    #create the reverse complement of the input strand, to get the coding strand
    #needed, because the .translate() function only translates from the coding strand
    if Is_Non_Coding_Strand:
        seq = seq.reverse_complement()
    #back transcribe mRNA to get the coding strand
    elif Is_mRNA:
        seq = seq.back_transcribe()
    #translation without stop symbols, to receive a uniform string without any breaks in between
    #return the Biopython sequence as a string, because that is the way the Protein_Structure_Prediction() function needs the input
    protein = seq.translate(stop_symbol = "")
    return str(protein)



#function mentioned in Additions/Improvements, for Blast API request
def Intron_Search_Database():
    pass

from Bio.Seq import Seq



def read():
    path = "C:/Users/leand/Downloads/"
    filename = "1a80.txt"
    file = open(path  + filename, "r")
    gene = file.read()
    #removing newlines \n and removing carriage return \r for formatting
    gene = gene.replace ("\n", "").replace("\r", "")

def coding_DNA_sequence_biosynthesis(gene):
    coding_dna = Seq(gene)
    mrna = coding_dna.transcribe()
    amino_acids = mrna.translate()
    return(mrna)
    return(amino_acids)
def genomic_DNA():
    pass

read()

if input == "CDS":
    coding_DNA_sequence_biosynthesis()
elif input == "genomic DNA without introns":
    genomic_DNA()
elif input == "genomic DNA with known introns":
    pass
else:
    print("An approach to typical intron structures will be made and they will be removed")
    pass

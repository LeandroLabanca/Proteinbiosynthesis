from Bio.Seq import Seq

def read():
    path = "C:/Users/leand/Downloads/"
    filename = "1a80.txt"
    file = open(path  + filename, "r")
    global gene
    gene = file.read()
    #removing newlines \n and removing carriage return \r for formatting
    gene = gene.replace ("\n", "").replace("\r", "")
    return gene

def non_coding_strand_to_coding_strand(): #helper function, to change from non coding to coding strand etc.
    global coding_strand
    global non_coding_strand
    noncoding_strand = gene
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

def coding_to_non_coding_strand(): #helper function for both GUI versions later
    global non_coding_strand
    global coding_strand
    coding_strand = gene
    non_coding_strand = ""
    for base in gene:
        if base == "A":
            non_coding_strand += "T"
        elif base == "C":
            non_coding_strand += "G"
        elif base == "G":
            non_coding_strand += "C"
        elif base == "T":
            non_coding_strand += "A"

def coding_DNA_sequence_biosynthesis(): #intron free
    coding_dna = Seq(coding_strand)
    mrna = coding_dna.transcribe()
    amino_acids = mrna.translate(stop_symbol=" ")
    print(amino_acids)
    return mrna, amino_acids

def genomic_DNA_with_known_introns():
    coding_dna = Seq(coding_strand)
    mrna = coding_dna.transcribe()
    global introns
    introns = []
    while True:
        user_input = input("Do you want to add introns? (y/n)")
        if user_input == "y":
            intron = input("Enter intron sequence")
            introns.append(intron)
        elif user_input == "n":
            break
        else:
            print("Enter a valid input")
    for intron in introns:
        if intron in mrna:
            mrna = mrna.replace(intron, "")
    amino_acids = mrna.translate()
    print(amino_acids)
    return mrna, amino_acids

def intron_search_database():
    pass














read()

dna_type = input("Is your sequence a coding strand, non coding strand or mrna")
if dna_type == "non coding strand":
    non_coding_strand_to_coding_strand() #for GUI and also translation
    print(coding_strand)
elif dna_type == "mrna":
    coding_strand = Seq(gene).back_transcribe()
else:
    coding_to_non_coding_strand() #for GUI

user_input = input("How's it looking for introns")
if user_input == "without introns": #already spliced and without introns
    coding_DNA_sequence_biosynthesis()
elif user_input == "genomic DNA with known introns": #manually input introns for splicing
    genomic_DNA_with_known_introns()
elif user_input == "genomic DNA with no known introns check Database NCBII": #check if gene/DNA is in database with introns removed, use that one
    pass
else:
    print("Everything gets translated such as CDS")
    coding_DNA_sequence_biosynthesis()

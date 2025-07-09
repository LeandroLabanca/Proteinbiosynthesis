from Bio.Seq import Seq



def read():
    path = "C:/Users/leand/Downloads/"
    filename = "1a80clean.txt"
    file = open(path  + filename, "r")
    global gene
    gene = file.read()
    #removing newlines \n and removing carriage return \r for formatting
    gene = gene.replace ("\n", "").replace("\r", "")
    return gene

def coding_DNA_sequence_biosynthesis():#actually input is non coding strand here, change before
    coding_dna = Seq(gene)
    mrna = coding_dna.transcribe()
    start_index = mrna.find("AUG")
    if start_index != -1:
        trimmed_mrna = mrna[start_index:]
        amino_acids = trimmed_mrna.translate()
    else:
        amino_acids = coding_dna.translate()
    print(amino_acids)
    return mrna, amino_acids



def genomic_DNA_with_known_introns():
    coding_dna = Seq(gene)
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




read()
user_input = input("type DNA type")

if user_input == "CDS": #already spliced and without introns
    coding_DNA_sequence_biosynthesis()
elif user_input == "genomic DNA with known introns": #manually input introns for splicing
    genomic_DNA_with_known_introns()
elif user_input == "genomic DNA with no known introns check Database NCBII": #check if gene/DNA is in database with introns removed, use that one
    pass
else:
    print("An approach to typical intron structures will be made and they will be removed")
    pass

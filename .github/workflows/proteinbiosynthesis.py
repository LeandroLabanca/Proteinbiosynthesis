from Bio.Seq import Seq

path = "C:/Users/leand/Downloads/"
filename = "1a80.txt"

file = open(path  + filename, "r")
gene = file.read()

gene = gene.replace ("\n", "")
gene = gene.replace("\r", "")

coding_DNA = Seq(gene)

mRNA = coding_DNA.transcribe()




#test





print(gene)
print(mRNA)

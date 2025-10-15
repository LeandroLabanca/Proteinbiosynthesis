#Numpy for creation of arrays with the data and labels/indices
import numpy as np
#function for splitting the dataset into training and validation sets
from sklearn.model_selection import train_test_split

#load the datasets downloaded. (Download link in sources in Documentation)
CB513 = np.load(r"C:\Users\leand\Downloads\cb513+profile_split1.npy.gz")
Cullpdb = np.load(r"C:\Users\leand\Downloads\cullpdb+profile_5926_filtered.npy.gz")

#reshaping datasets, so they fit the input size, defined for the model.
#if the protein is longer than 700 residues, it will be truncated->residues removed from the end.
#if the protein is shorter than 700 residues, the rest will be padded->filled up with zeros, to ensure uniform length.
#514 proteins in CB513 and 5365 in CullPDB dataset
CB513 = CB513.reshape((514, 700, 57))
Cullpdb = Cullpdb.reshape((5365, 700, 57))

#extract amino acid features and secondary structure labels for CB513
X_Cb = CB513[:, :, 0:20] #20 amino acids
Secondary_Structure_Channels = CB513[:, :, 22:31] #8 secondary structures
Y_Cb = np.argmax(Secondary_Structure_Channels, axis= -1)

#extract amino acid features and secondary structure labels for CullPDB
X_Cp = Cullpdb[:, :, 0:20]
Secondary_Structure_Channels = Cullpdb[:, :, 22:31]
Y_Cp = np.argmax(Secondary_Structure_Channels, axis= -1)

#changing DSSP 8-class secondary structure labels to 3-class secondary structure labels (Helix, Strand, Coil)
def Dssp8_To_Dssp3(y):
    Y3 = np.copy(y)
    Y3[np.isin(y, [0,3,4])] = 0
    Y3[np.isin(y, [1, 2])] = 1
    Y3[np.isin(y, [5, 6, 7, 8])] = 2
    return Y3
Y_Cb = Dssp8_To_Dssp3(Y_Cb)
Y_Cp = Dssp8_To_Dssp3(Y_Cp)

#split CullPDB test set into the training (90%) and validation sets (10%)
#used for model training and validation accuracy after each epoch
X_Train, X_Validation, Y_Train, Y_Validation = train_test_split(X_Cp, Y_Cp, test_size=0.1, random_state=42)


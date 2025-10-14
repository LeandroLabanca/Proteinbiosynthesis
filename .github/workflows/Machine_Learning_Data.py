import numpy as np
from sklearn.model_selection import train_test_split

CB513 = np.load(r"C:\Users\leand\Downloads\cb513+profile_split1.npy.gz")
Cullpdb = np.load(r"C:\Users\leand\Downloads\cullpdb+profile_5926_filtered.npy.gz")

CB513 = CB513.reshape((514, 700, 57))
Cullpdb = Cullpdb.reshape((5365, 700, 57))

X_Cb = CB513[:, :, 0:20]
Secondary_Structure_Channels = CB513[:, :, 22:31]
Y_Cb = np.argmax(Secondary_Structure_Channels, axis= -1)

X_Cp = Cullpdb[:, :, 0:20]
Secondary_Structure_Channels = Cullpdb[:, :, 22:31]
Y_Cp = np.argmax(Secondary_Structure_Channels, axis= -1)

def Dssp9_To_Dssp3(y):
    Y3 = np.copy(y)
    Y3[np.isin(y, [0,3,4])] = 0
    Y3[np.isin(y, [1, 2])] = 1
    Y3[np.isin(y, [5, 6, 7, 8])] = 2
    return Y3
Y_Cb = Dssp9_To_Dssp3(Y_Cb)
Y_Cp = Dssp9_To_Dssp3(Y_Cp)

X_Train, X_Validation, Y_Train, Y_Validation = train_test_split(X_Cp, Y_Cp, test_size=0.1, random_state=42)


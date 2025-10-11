import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf
from collections import Counter


Amino_Acids = 'ACDEFGHIKLMNPQRSTVWY'
Amino_Acid_To_Index = {aa: Idx for Idx, aa in enumerate(Amino_Acids)}

Index_To_Label = {0: 'H', 1: 'E', 2: 'C'}

def Clean_Sequence(seq):
    Valid = set(Amino_Acid_To_Index)
    Cleaned = ''.join([aa for aa in seq if aa in Valid])
    Invalid = set(seq) - Valid
    if Invalid:
        print(f"Invalid amino acids in input: {Invalid}")
    return Cleaned

def One_Hot_Encode_Protein(seq, Max_Len = 700):
    Encoding = np.zeros((Max_Len, 20), dtype = np.float32)
    for i, aa in enumerate(seq[:Max_Len]):
        Idx = Amino_Acid_To_Index.get(aa)
        if Idx is not None and 0 <= Idx < 20:
            Encoding[i, Idx] = 1.0
        else:
            print(f"Warning: unknown amino acid '{aa}' at position {i} - skipped.")
            continue
    return Encoding

Model = load_model("Secondary_Structure_Model.keras")

def Protein_Structure_Prediction(amino_acids):
    Protein = Clean_Sequence(amino_acids)
    print(f"Cleaned sequence length: {len(Protein)}")
    Encoded_Protein = One_Hot_Encode_Protein(Protein)
    Input_Batch = np.expand_dims(Encoded_Protein, axis = 0)

    Predictions = Model.predict(Input_Batch)
    Predicted_Classes = tf.argmax(Predictions, axis = -1).numpy()[0]

    Predicted_Labels = ''.join([Index_To_Label[i]for i in Predicted_Classes[:len(Protein)]])
    Counts = Counter(Predicted_Labels)
    return Protein, Predicted_Labels, Counts

import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf
from collections import Counter

#define valid amino acids, setting indexes to individual ones
Amino_Acids = 'ACDEFGHIKLMNPQRSTVWY'
Amino_Acid_To_Index = {aa: Idx for Idx, aa in enumerate(Amino_Acids)}

#create dictionary with the labels for each index, to visually represent each structure type
Index_To_Label = {0: 'H', 1: 'E', 2: 'C'}

#clean invalid amino acids, to avoid errors in input to the model
def Clean_Sequence(seq):
    Valid = set(Amino_Acid_To_Index)
    Cleaned = ''.join([aa for aa in seq if aa in Valid])
    Invalid = set(seq) - Valid
    if Invalid:
        print(f"Invalid amino acids in input: {Invalid}")
    return Cleaned

#define one-hot-encoding for the amino acids, to give each amino acid its own index, for the input into the machine learning model
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

#load the previously trained secondary structure prediction model
Model = load_model("Secondary_Structure_Model.keras")

#predict protein secondary structure of the translated input biological sequence
def Protein_Structure_Prediction(amino_acids):
    Protein = Clean_Sequence(amino_acids)
    print(f"Cleaned sequence length: {len(Protein)}")
    Encoded_Protein = One_Hot_Encode_Protein(Protein)
    Input_Batch = np.expand_dims(Encoded_Protein, axis = 0)

    #actual prediction, using the .predict function from tensorflow
    Predictions = Model.predict(Input_Batch)
    Predicted_Classes = tf.argmax(Predictions, axis = -1).numpy()[0]

    #convert predicted calss indices into structure labels (H; helix, E; strand, C; coil)
    Predicted_Labels = ''.join([Index_To_Label[i] for i in Predicted_Classes[:len(Protein)]])
    Counts = Counter(Predicted_Labels)
    #return the cleaned sequence, string of predicted structures and counts for each structure
    return Protein, Predicted_Labels, Counts

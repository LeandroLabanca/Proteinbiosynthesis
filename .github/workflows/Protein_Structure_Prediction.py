import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf
from collections import Counter


Amino_Acids = 'ACDEFGHIKLMNPQRSTVWY'
amino_acid_to_index = {aa: idx for idx, aa in enumerate(Amino_Acids)}

index_to_label = {0: 'H', 1: 'E', 2: 'C'}

def one_hot_encode_protein(seq, max_len = 700):
    encoding = np.zeros((max_len, 20), dtype = np.float32)
    for i, aa in enumerate(seq[:max_len]):
        idx = amino_acid_to_index.get(aa)
        if idx is not None and 0 <= idx < 20:
            encoding[i, idx] = 1.0
        else:
            print(f"Warning: unknown amino acid '{aa}' at position {i} - skipped.")
            continue
    return encoding

def clean_sequence(seq):
    valid = set(amino_acid_to_index)
    cleaned = ''.join([aa for aa in seq if aa in valid])
    invalid = set(seq) - valid
    if invalid:
        print(f"Invalid amino acids in input: {invalid}")
    return cleaned

model = load_model("Secondary_Structure_Model.keras")

def Protein_Structure_Prediction(amino_acids):
    protein = clean_sequence(amino_acids)
    print(f"Cleaned sequence length: {len(protein)}")
    encoded_protein = one_hot_encode_protein(protein)
    input_batch = np.expand_dims(encoded_protein, axis = 0)

    predictions = model.predict(input_batch)
    predicted_classes = tf.argmax(predictions, axis = -1).numpy()[0]

    predicted_labels = ''.join([index_to_label[i]for i in predicted_classes[:len(protein)]])
    counts = Counter(predicted_labels)
    return protein, predicted_labels, counts

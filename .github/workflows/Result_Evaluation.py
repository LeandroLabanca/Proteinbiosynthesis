import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score
from tensorflow.keras.models import load_model
import tensorflow as tf

from Machine_Learning_Data import x_cb, y_cb

index_to_label = {0: 'H', 1: 'E', 2: 'C'}
labels =['H', 'E', 'C']

model = load_model('Secondary_Structure_Model.keras')
print("Model loaded. Evaluating on CB513...")

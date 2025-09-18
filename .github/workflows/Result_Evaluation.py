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

predictions = model.predict(x_cb, verbose=1)
pred_classes = tf.argmax(predictions, axis=-1).numpy()

y_true = y_cb.flatten()
y_pred = pred_classes.flatten()

mask = y_true != -1
y_true = y_true[mask]
y_pred = y_pred[mask]

acc = accuracy_score(y_true, y_pred)
print(f'Overall Accuracy on CB513: {acc * 100:.2f}%')

cm = confusion_matrix(y_true, y_pred, labels = [0,1,2])
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

plt.figure(figsize=(6,5))
sns.heatmap(cm_normalized, annot=True, cmap='Blues', xticklabels=labels, yticklabels=labels, fmt='.2f')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Normalized Confusion Matrix (CB513)')
plt.show()

per_class_acc = cm.diagonal()/cm.sum(axis=1)
plt.figure(figsize=(6,4))
sns.barplot(x=labels, y=per_class_acc*100)
plt.ylabel('Accuracy (%)')
plt.title('Per-Class Accuracy on CB513')
plt.show()

true_lengths = (y_cb !=-1).sum(axis=1)
correct_per_protein = (pred_classes ==y_cb).sum(axis=1)
acc_per_protein = correct_per_protein / true_lengths

plt.figure(figsize=(7,5))
plt.scatter(true_lengths, acc_per_protein, alpha=0.6)
plt.xlabel('Protein Length')
plt.ylabel('Accuracy')
plt.title('Prediction Accuracy vs Protein Length (CB513)')
plt.show()
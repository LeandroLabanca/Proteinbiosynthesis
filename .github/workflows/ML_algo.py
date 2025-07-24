from Machine_Learning_Data import x_train, y_train, x_validation, y_validation, x_cb, y_cb
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, Dropout, TimeDistributed, Dense

ML_Model = Sequential([
    Conv1D(64, kernel_size=7, padding='same', activation='relu', input_shape=(700, 20)),
    Dropout(0.3),
    Conv1D(64, kernel_size=7, padding='same', activation='relu'),
    Dropout(0.3),
    TimeDistributed(Dense(3, activation='softmax')),
])

ML_Model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
ML_Model.fit(x_train, y_train, validation_data=(x_validation, y_validation), epochs=10, batch_size=32)

ML_Model.evaluate(x_cb, y_cb)

ML_Model.save("Secondary_Structure_Model.h5")

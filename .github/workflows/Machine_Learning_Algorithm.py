from Machine_Learning_Data import X_Train, Y_Train, X_Validation, Y_Validation, X_Cb, Y_Cb
#import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, Dropout, TimeDistributed, Dense

Machine_Learning_Model = Sequential([
    Conv1D(64, kernel_size=7, padding='same', activation='relu', input_shape=(700, 20)),
    Dropout(0.3),
    Conv1D(64, kernel_size=7, padding='same', activation='relu'),
    Dropout(0.3),
    TimeDistributed(Dense(3, activation='softmax')),
])

Machine_Learning_Model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
Machine_Learning_Model.fit(X_Train, Y_Train, validation_data=(X_Validation, Y_Validation), epochs=10, batch_size=32)

Machine_Learning_Model.evaluate(X_Cb, Y_Cb)

Machine_Learning_Model.save("Secondary_Structure_Model.keras")

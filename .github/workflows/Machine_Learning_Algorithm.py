from Machine_Learning_Data import X_Train, Y_Train, X_Validation, Y_Validation, X_Cb, Y_Cb
#import the model type and the layers used
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, Dropout, TimeDistributed, Dense

#define the model with 2 convolutional and dropout layers and 1 dense layer.
Machine_Learning_Model = Sequential([
    #64 filters and kernel size 7 for the layer, to capture local sequence patterns of residues, with activated padding
    Conv1D(64, kernel_size=7, padding='same', activation='relu', input_shape=(700, 20)),
    #30% of nodes are randomly deactivated each training step
    Dropout(0.3),
    Conv1D(64, kernel_size=7, padding='same', activation='relu'),
    Dropout(0.3),
    #in dense layers all nodes are connected
    TimeDistributed(Dense(3, activation='softmax')),
])

#compiling the machine learning model (actually deep learning model as per definition)
Machine_Learning_Model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

#training the model on the input data over 10 epochs and using validation set for each epoch
Machine_Learning_Model.fit(X_Train, Y_Train, validation_data=(X_Validation, Y_Validation), epochs=10, batch_size=32)

#evaluate on independent test model CB513
Machine_Learning_Model.evaluate(X_Cb, Y_Cb)

#save the model as a .keras file, so it can be loaded later in the GUI application
Machine_Learning_Model.save("Secondary_Structure_Model.keras")


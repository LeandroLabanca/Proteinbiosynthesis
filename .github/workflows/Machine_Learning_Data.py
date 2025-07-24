import numpy as np
from sklearn.model_selection import train_test_split

cb513 = np.load(r"C:\Users\leand\Downloads\cb513+profile_split1.npy.gz")
cullpdb = np.load(r"C:\Users\leand\Downloads\cullpdb+profile_5926_filtered.npy.gz")

cb513 =cb513.reshape((514, 700, 57))
cullpdb = cullpdb.reshape((5365, 700, 57))

x_cb = cb513[:, :, 0:20]
ss_channels = cb513[:, :, 22:31]
y_cb = np.argmax(ss_channels, axis= -1)

x_cp = cullpdb[:, :, 0:20]
ss_channels = cullpdb[:, :, 22:31]
y_cp = np.argmax(ss_channels, axis= -1)

x_train, x_validation, y_train, y_validation = train_test_split(x_cp, y_cp, test_size=0.1, random_state=42)


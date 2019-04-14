import os
import copy
import pickle
import pandas as pd
import numpy as np

# Preprocessers
import preprocess.audio_preprocesser as ap

# feature extractoring and preprocessing data
import csv
import pandas as pd
import numpy as np

# Sklearn helpers
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.metrics import classification_report, precision_score, recall_score

# Keras
from keras import models
from keras import layers
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import rmsprop
from tools import f1

data_dir = "../data/"
data_file = 'genre_info.csv'
trained_dir = '../data/trained'

# Use CNN spectrogram model
IMG_SIZE = 256
NUM_CLASSES = 10

print('Loading data...')
data = pd.read_csv(os.path.join(data_dir, data_file), encoding="ISO-8859-1")
print('---- orig data shape: {}'.format(data.shape))

# Drop unnecessary columns
data = data.drop(['filename'], axis=1)

# Encode each genre with a corresponding label
# **One hot encoding
print('Transforming and normalizing data...')
genre_list = data.iloc[:, -1]
encoder = LabelEncoder()

y = encoder.fit_transform(genre_list)
print('---- labels: {}'.format(encoder.classes_))

# Scale features to normalize
scaler = StandardScaler()
X = scaler.fit_transform(np.array(data.iloc[:, :-1], dtype=float))

# *** Save TRAINED Feature Extractor ***
if not os.path.isfile(os.path.join(trained_dir, 'genre_encoder.pkl')):
    with open(os.path.join(trained_dir, 'genre_encoder.pkl'), 'wb') as f:
        pickle.dump(encoder, f)
if not os.path.isfile(os.path.join(trained_dir, 'genre_scaler.pkl')):
    with open(os.path.join(trained_dir, 'genre_encoder.pkl'), 'wb') as f:
        pickle.dump(scaler, f)

# Set up Data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=1998)

# Set up keras classifier
model = models.Sequential()
model.add(Conv2D(64, (3, 3),
                    activation='relu',
                    padding='same',
                    input_shape=(IMG_SIZE, IMG_SIZE, 1)))
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(100, 100, 3)))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(128, (3, 3),
                    activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(256, (3, 3),
                    activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(512, (3, 3),
                    activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(1024, (3, 3),
                    activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.5))
model.add(Flatten())
model.add(Dense(500, activation='relu'))
model.add(Dense(NUM_CLASSES, activation='softmax'))

# initiate RMSprop optimizer > ADAM
opt = rmsprop(lr=0.0001, decay=1e-6)
model.compile(loss='categorical_crossentropy',
                optimizer=opt,
                metrics=[f1])

# Form the model and fit
print('Fitting model....')
history = model.fit(X_train, y_train, epochs=20, batch_size=128)

# Show results
test_loss, test_acc = model.evaluate(X_test, y_test)

# Get detailed classification scores
y_pred_conf = model.predict(X_test)
y_pred = [np.argmax(row) for row in y_pred_conf]

report = classification_report(y_test, y_pred)
print(report)

y_test = y_test.tolist()

with open(os.path.join('../data/results/', 'results.txt'), 'w') as f:
    f.write('------------TRUTH vs. PREDICTS------------\n')
    f.writelines(['{} {}\n'.format(y_test[i], y_pred[i])
                  for i in range(len(y_test))])
    f.write(report)

# *** Save TRAINED model ***
model.save(os.path.join(trained_dir, 'genre_model.h5'))

print('Starting 10-Fold validation...')
kf = KFold(n_splits=10)
avg_p = 0
avg_r = 0
count = 0

for train, test in kf.split(X):
    history = model.fit(X[train], y[train], epochs=20, batch_size=128, verbose=0)

    # Predict
    y_pred_conf = model.predict(X[test])
    y_pred = [np.argmax(row) for row in y_pred_conf]

    print("Fold {} -----------------------------".format(count))
    print(classification_report(y[test], y_pred))
    count+=1
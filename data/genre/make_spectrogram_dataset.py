# Modified version of https://github.com/carl03q/AudioClassifier/blob/master
# Make the spectrogram dataset from the GTZAN genre collection

import os
import pickle
import numpy as np
from PIL import Image
from random import shuffle

input_path = './img_data/'
IMG_SIZE = 256

data = []

# genre folders
genres = os.listdir(input_path)

with open('label_map.txt', 'w') as f:
    for i, genre in enumerate(genres):
        f.write('{} - {}'.format(i, genre))
        genre_dir = input_path + genre +'/'
        
        files = os.listdir(genre_dir)
        for file in files:
            file_dir = genre_dir + file
            print("Processing ", file_dir)
            im = Image.open(file_dir).convert('L')

            # 2D Array --> Future can try 3D with RGB colors in spectrogram
            imgData = np.asarray(im, dtype=np.uint8).reshape(IMG_SIZE, IMG_SIZE, 1)
            imgData = imgData / 255 # normalize pixels

            # Label <-- one hot vector
            label = [0 for genre in range(len(genres))]
            label[i] = 1
            data.append((imgData, label))

shuffle(data)
x, y = zip(*data)
X = np.array(x[:]).reshape([-1, IMG_SIZE, IMG_SIZE, 1])
y = np.array(y[:])

print("Saving dataset... ")
pickle.dump(X, open("genre_data.p", "wb"))
pickle.dump(y, open("genre_labels.p", "wb"))
print("Dataset saved.")
import os
import pickle
import pandas
from preprocess import audio_preprocesser
from keras.models import load_model

trained_dir = '../data/trained'
encoder_file = 'genre_encoder.pkl'
scaler_file = 'genre_scaler.pkl'
model_file = 'nn_genre_model.h5'


with open(os.path.join(trained_dir, encoder_file), 'rb') as f:
    encoder = pickle.load(f)
with open(os.path.join(trained_dir, scaler_file), 'rb') as f:   
    scaler = pickle.load(f)
model = load_model(os.path.join(trained_dir, model_file))

import os
import pickle
import pandas
from preprocess import lyrics_preprocesser, audio_preprocesser

trained_dir = '../data/trained'
model_file = 'popularity_model.pkl'
funion_file = 'popularity_funion.pkl'

model = pickle.load(os.path.join())

def predict(audio_file, lyrics):
    pass
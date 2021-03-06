import os
import copy
import pickle
import pandas as pd
import numpy as np
import matplotlib

# Preprocessers
from tools import get_song_info, process_lyrics_col

# Sklearn helpers
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import FeatureUnion, Pipeline

# Model
# from sklearn.SVM import SVR
# from sklearn.kernel_ridge import KernelRidge
# from sklearn.neural_network import MLPRegressor
import xgboost as xgb

data_dir = "../data"
data_lyrics_dir = data_dir + "/lyrics"
trained_dir = data_dir + '/trained'
data_file = 'song_info.csv'

print('Loading data...')
data = pd.read_csv(os.path.join(data_dir, data_file), encoding="ISO-8859-1")

# Drop missing and unused data
data = data.dropna(axis=0, how='any')

# Get ground truth
y = copy.deepcopy(data.song_popularity)

data = data.drop("song_popularity", axis=1)
data = data.values.tolist()

# Join lyrics as stemmed words list for each song
print("Starting feature extraction...")
MAX_FEATURES = 10000

feats_union = FeatureUnion([ 
    ('count_feats', Pipeline([
        ('process_lyrics', FunctionTransformer(process_lyrics_col, validate=False)),
        ('count', CountVectorizer(analyzer="word", ngram_range=(1,1),strip_accents='unicode', max_features=MAX_FEATURES)),
        ('feat_sel', SelectPercentile(f_classif, percentile=20))
    ])),
    # ('tfidf_feats', Pipeline([
        # ('tfidf_v', TfidfVectorizer(analyzer='word', sublinear_tf=True, strip_accents='unicode', ngram_range=(1, 1), max_features=MAX_FEATURES)),
        # ('feat_sel', SelectPercentile(f_classif, percentile=50))
    # ])),
    ('info', FunctionTransformer(get_song_info, validate=False))
])

X = feats_union.fit_transform(data, y)

# *** Save TRAINED Feature Extractor ***
with open(os.path.join(trained_dir, 'popularity_funion.pkl'), 'wb') as f:
    pickle.dump(feats_union, f)

print('---- data shape: {}'.format(X.shape))

# Start training
print("Start training and predict...")
regressor = xgb.XGBRegressor(objective="reg:linear", random_state=1998)


# Saving model trained on data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=2019)
model = regressor.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)
nMSE = mean_squared_error(y_test, y_pred) / np.mean(np.square(y_test))
print("---- model achieved nMSE of {}".format(nMSE))

y_pred = y_pred.tolist()
y_test = y_test.tolist()
with open(os.path.join('../data/results/', 'results.txt'), 'w') as f:
    f.write('------------TRUTH vs. PREDICTS------------\n')
    f.writelines(['{} {}\n'.format(y_test[i], y_pred[i]) for i in range(len(y_test))])

# *** Save TRAINED model ***
with open(os.path.join(trained_dir, 'popularity_model.pkl'), 'wb') as f:
    pickle.dump(model, f)

# Start Validation
print("Starting 10-Fold validation...")
nMSEs = []
kf = KFold(n_splits=10)

# Mimic KFold splits
for fold in range(10):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    model = regressor.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)
    nMSE = mean_squared_error(y_test, y_pred) / np.mean(np.square(y_test))
    nMSEs.append(nMSE)

    print("Round %d/10 of nMSE is: %f" %(fold+1, nMSE))
    
print('Average nMSE is %f' %(np.mean(nMSEs)))




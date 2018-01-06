import csv
import numpy as np
from sklearn import linear_model
from sklearn.externals import joblib

train_data_g2 = []
train_data_g4 = []
train_data_g6 = []
train_data_g8 = []
train_data_g0 = []
train_data_x2 = []
train_data_x4 = []
train_data_x6 = []
train_data_x8 = []
train_data_x0 = []
train_label = []

with open('pergold1.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        train_data_g2.append(int(row['rg2']))
        train_data_g4.append(int(row['rg4']))
        train_data_g6.append(int(row['rg6']))
        train_data_g8.append(int(row['rg8']))
        train_data_g0.append(int(row['rg10']))
        train_data_x2.append(int(row['rx2']))
        train_data_x4.append(int(row['rx4']))
        train_data_x6.append(int(row['rx6']))
        train_data_x8.append(int(row['rx8']))
        train_data_x0.append(int(row['rx10']))
        train_label.append(float(row['rwin']))

train_data_g2 = np.expand_dims(np.asarray(train_data_g2), 1)
train_data_g4 = np.expand_dims(np.asarray(train_data_g4), 1)
train_data_g6 = np.expand_dims(np.asarray(train_data_g6), 1)
train_data_g8 = np.expand_dims(np.asarray(train_data_g8), 1)
train_data_g0 = np.expand_dims(np.asarray(train_data_g0), 1)
train_data_x2 = np.expand_dims(np.asarray(train_data_x2), 1)
train_data_x4 = np.expand_dims(np.asarray(train_data_x4), 1)
train_data_x6 = np.expand_dims(np.asarray(train_data_x6), 1)
train_data_x8 = np.expand_dims(np.asarray(train_data_x8), 1)
train_data_x0 = np.expand_dims(np.asarray(train_data_x0), 1)
train_label = np.asarray(train_label)

LR_g2 = linear_model.LogisticRegression(C=1e5).fit(train_data_g2, train_label)
LR_g4 = linear_model.LogisticRegression(C=1e5).fit(train_data_g4, train_label)
LR_g6 = linear_model.LogisticRegression(C=1e5).fit(train_data_g6, train_label)
LR_g8 = linear_model.LogisticRegression(C=1e5).fit(train_data_g8, train_label)
LR_g0 = linear_model.LogisticRegression(C=1e5).fit(train_data_g0, train_label)
LR_x2 = linear_model.LogisticRegression(C=1e5).fit(train_data_x2, train_label)
LR_x4 = linear_model.LogisticRegression(C=1e5).fit(train_data_x4, train_label)
LR_x6 = linear_model.LogisticRegression(C=1e5).fit(train_data_x6, train_label)
LR_x8 = linear_model.LogisticRegression(C=1e5).fit(train_data_x8, train_label)
LR_x0 = linear_model.LogisticRegression(C=1e5).fit(train_data_x0, train_label)

joblib.dump(LR_g2, 'models/LR_g2.pkl')
joblib.dump(LR_g4, 'models/LR_g4.pkl')
joblib.dump(LR_g6, 'models/LR_g6.pkl')
joblib.dump(LR_g8, 'models/LR_g8.pkl')
joblib.dump(LR_g0, 'models/LR_g0.pkl')
joblib.dump(LR_x2, 'models/LR_x2.pkl')
joblib.dump(LR_x4, 'models/LR_x4.pkl')
joblib.dump(LR_x6, 'models/LR_x6.pkl')
joblib.dump(LR_x8, 'models/LR_x8.pkl')
joblib.dump(LR_x0, 'models/LR_x0.pkl')

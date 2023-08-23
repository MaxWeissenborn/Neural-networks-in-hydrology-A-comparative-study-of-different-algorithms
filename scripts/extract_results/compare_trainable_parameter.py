#import tensorflow.keras.backend as K
from tensorflow.keras.models import load_model
from keras.utils.layer_utils import count_params
import pickle
from pathlib import Path


path = "../../df_best_runs.pkl"
prefix = 2

with open(path, "rb") as f:
    best_models = pickle.load(f)
print(best_models.to_string())

result = {}
for row in best_models.itertuples():
    p = row.path
    p = Path(p).parent.parent
    p = p.joinpath(row.model)

    model = load_model(p, compile=False)
    print(row.modelBS, ", ", count_params(model.trainable_weights))
    #print(count_params(model.trainable_weights))
    #print(model.summary())


# some models were created with older versions of tensorflow and are now unable to load correctly
# CNN +ESF BS=256 ,  3230545
# LSTM +ESF BS=256 ,  649776
# CNN +ESF BS=2048 ,  17070619
# GRU +ESF BS=256 ,  611784
# CNN -SF BS=256 ,  17361573
# GRU +ESF BS=2048 ,  587637
# LSTM -SF BS=256 ,  593268
# GRU -SF BS=256 ,  644940
# LSTM +ESF BS=2048 ,  244020
# CNN -SF BS=2048 ,  18525716
# GRU -SF BS=2048 ,  577265
# LSTM -SF BS=2048 ,  152278

"""compare of 3 best lineplots
and 3 worst lineplots
"""
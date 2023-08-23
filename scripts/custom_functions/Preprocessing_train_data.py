import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
import os


def remove_whitespace(data):
    for i in data.columns:
        # checking datatype of each columns
        if data[i].dtype == 'object':
            # applying strip function on column
            data[i] = data[i].map(str.strip)
    return data


def match_duplicates(data, col):
    """
    unique soil types are
    ['Dystric Cambisols', 'Eutric Cambisols / Stagnic Gleysols', 'Eutric Cambisols',
     'Haplic Luvisols / Eutric Podzoluvisols / Stagnic Gleysols', 'Spodic Cambisols', 'Spodic Cambisol']
     'Spodic Cambisols' is the same as 'Spodic Cambisol', so an additional 's' is needed
    """

    data[col] = np.where(data[col].str[-1] != "s", data[col] + "s", data[col])
    return data


def load_data(filename):
    # load in data
    dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
    df = pd.read_csv(Path.joinpath(input_path, filename), sep=";", date_parser=dateparse, index_col="date")

    print(filename, "data has the following shape:", df.shape)

    return df


def remove_na(data, filename):
    # creating dataset of rivers with no missing values
    print(len(data.columns[data.isna().any()].tolist()), "Columns have missing values and will be removed.")
    df_no_na = data.drop(data.columns[data.isna().any()], axis=1)
    print("data has now the following shape:", df_no_na.shape)
    return save(df_no_na, filename)


def save(data, filename):
    # save new data file
    # data.to_csv(Path.joinpath(output_path, 'NO NA ' + filename), encoding='utf-8')
    return data


desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns', 20)

base = Path().resolve().parent.parent

input_path = Path.joinpath(base, "preprocessing", "raw data")
output_path = Path.joinpath(base, "preprocessing", "output")
if not os.path.isdir(output_path):
    os.makedirs(output_path)

add_static_features = False

if add_static_features:
    prefix = "+ESF"
else:
    prefix = "-SF"

filenames = ["et_mm_1991_2018_corrected.csv",
             "prec_mm_1991_2018.csv",
             "soil_temp_C_1991_2018.csv",
             "dis_mm_1991_2018.csv"]

river_data = {}
for f in filenames:
    df = load_data(f)
    df = remove_na(df, f)
    print(df.shape)
    river_data["_".join(f.split("_")[:2])] = df
0/0
# load in catchmant data
df_catchment = pd.read_csv(Path.joinpath(input_path, "cleaned_catchment_attributes_num.csv"), sep=";")
# remove redundant whitespace
df_catchment = remove_whitespace(df_catchment)
# make sure ever soil type ends with an "s" to prevent duplicates
df_catchment = match_duplicates(df_catchment, "dominating_soil_type_bk500")

df_catchment.drop(['gauge',
                   'leitercharackter_huek250',
                   # 'gesteinsart_huek250',
                   # 'soil_texture_boart_1000',
                   # 'durchlässigkeit_huek250',
                   # 'dominating_soil_type_bk500',
                   'dis_mean',
                   # 'runoff_ratio',
                   'grundwasserneubildung_gwn_1000',
                   # 'greundigkeit_physgru_1000'
                   ], axis=1, inplace=True)

print(df_catchment.isna().sum())

# remove rows with missing data
idx = df_catchment[df_catchment['et_mean'].isnull()].index
df_catchment = df_catchment.drop(idx, axis=0)

###############################
# New extended static feature #
###############################

# Label Encoding
cols = ['gesteinsart_huek250', 'soil_texture_boart_1000', 'durchlässigkeit_huek250', 'dominating_soil_type_bk500',
        "land_use_corine"]
_ = {}
for category in cols:
    print(category)
    le = LabelEncoder()
    le.fit(df_catchment[category])
    print(le.classes_)
    _[category] = {i: l for i, l in enumerate(le.classes_)}
    df_catchment[category] = le.fit_transform(df_catchment[category])
print(_)
0/0
df_catchment.to_csv(Path.joinpath(output_path, "NO NA cleaned_catchment_attributes_num.csv"),
                    encoding='utf-8', index=False)

if not add_static_features:
    df_catchment.drop(
        ['gesteinsart_huek250', 'soil_texture_boart_1000', 'durchlässigkeit_huek250', 'dominating_soil_type_bk500',
         'runoff_ratio', 'greundigkeit_physgru_1000'], axis=1, inplace=True)

# one Hot Encoding
# cols = ['gesteinsart_huek250','soil_texture_boart_1000','durchlässigkeit_huek250','dominating_soil_type_bk500']
# df_catchment = pd.get_dummies(df_catchment, columns=cols)

###################################
# END New extended static feature #
###################################

# encode landuse
# print(df_catchment["land_use_corine"].unique())
# df_catchment = pd.get_dummies(df_catchment, columns=["land_use_corine"])

# get unique catchment id
catchments = df_catchment["gauge_id"].unique()

# make gauge_id new index of catchment dataframe
df_catchment.set_index('gauge_id', inplace=True)

# create dataframe for every catchment containing all attributes of filenames as columns
df_dict = {}
for c in catchments:
    str_c = str(c)
    temp_df = pd.DataFrame()
    for k, v in river_data.items():
        if str_c in river_data[k].columns:
            temp_df[k] = river_data[k][str_c]

    if len(temp_df.columns) > 3:
        df_dict[c] = temp_df

# print(len(df_dict))

final_data_dict = {}
if add_static_features:
    """
    get all column names of catchment data set. loop over river data sets to get every river id and the corresponding
    river data. Fetch the data from catchment dataset which is one row for every river. Repeat this line n times 
    for every day. Concat it with river data to gain one data set for every river with all information. Store every 
    data set in a dictionary with k = gauge_id and value = dataframe
    """

    new_cols = list(df_catchment.columns)
    for k, v in df_dict.items():
        temp_df = pd.DataFrame(np.repeat(df_catchment.loc[k].values[np.newaxis, ...], v.shape[0], axis=0),
                               columns=new_cols)
        temp_df_concat = pd.concat([v, temp_df.set_index(v.index)], axis=1, ignore_index=False)
        final_data_dict[k] = temp_df_concat

if len(final_data_dict) == 0:
    final_data_dict = df_dict

# show 1 example river
sample = list(final_data_dict.keys())[0]
print(final_data_dict[sample])

print("There are %s rivers in this data set" % len(final_data_dict))
shape_ = final_data_dict[sample].shape
print("The data set has Information for %s days or %s years" % (shape_[0], int(shape_[0] / 365)))
print(final_data_dict[sample].shape)
pickle.dump(final_data_dict, open(Path.joinpath(output_path, "%s - NO NA Complete River Data.pkl" % prefix), "wb"))

#################################################################################
# Combine all rivers to one dataset with a new column representing the river id #
#################################################################################

# create new column in every dataframe with gauge_id as value
for k, df in final_data_dict.items():
    df["gauge_id"] = k

# concat all dataframes
df_concat = pd.concat(tuple(final_data_dict[i] for i in [*final_data_dict]))

pickle.dump(df_concat, open(Path.joinpath(output_path,
                                          "%s - NO NA Complete River Data as Dataframe.pkl" % prefix), "wb"))

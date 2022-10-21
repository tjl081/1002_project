import pandas as pd
import json
from bson.json_util import dumps # converts mongodb cursor into python suitable 
import os
from pymongo import MongoClient # pip install "pymongo[srv]"
from datetime import datetime
import category_encoders as ce
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import preprocessing
import numpy as np


def get_db():
    """helper function, returns the resale price table as an object to run operations (like querying) on"""
    PATH = os.getcwd() + '\\data\\'
    CONNECTION_STR = ""
    with open(PATH + '/access_url.txt', 'r') as f:
        CONNECTION_STR = f.readline()
    print(CONNECTION_STR)
    initial_time = datetime.now()
    client = MongoClient(CONNECTION_STR)
    print(f"Connected to MongoDB client in {(datetime.now() - initial_time).total_seconds()}")
    db = client.test
    db_object = db["resale_prices"]

    return db_object

def remove_columns(df, column_name_list):
    """helper function. takes in a dataframe and a list of column names to remove from the dataframe. 
    can gracefully handle column names that do not exist. returns the updateed dataframe."""
    for col in column_name_list:
        if col in df.columns:
            df = df.drop(col, axis=1)
        else:
            print(f"'{col}' column not found. skipping...")
    return df

def process_ml_data(df):
    """Helper function, fills up null values, standardises column data"""
    middle_floor_value = lambda min_floor_str, max_floor_str : int((int(max_floor_str) + int(min_floor_str)) / 2)
    initial_time = datetime.now()
    counter = 1
    for index, row in df.iterrows():
        print(f"Iterating through row:{counter}")
        counter += 1
        if "year" in str(row['remaining_lease']):
            # if remaining_lease contains words
            remaining_lease_text_list = row["remaining_lease"].split(" ") # split x years y months to ["x", "years", "y", "months"]
            lease_duration_left = int(remaining_lease_text_list[0])

            if len(remaining_lease_text_list) == 4 and "month" in remaining_lease_text_list[3]:  # if a month value is detected in the row
                if int(remaining_lease_text_list[2]) > 7:
                    lease_duration_left += 1
            df.at[index,'remaining_lease'] = lease_duration_left
            
        elif pd.isnull(row['remaining_lease']):
            # take lease commence date + 99 years, then take the result year and deduct by current year
            lease_end_year  = int(row["lease_commence_date"]) + 99
            year_month_pair = row["month"].split("-")
            current_year = int(year_month_pair[0]) + int(int(year_month_pair[1]) > 7) # if the current date is 2nd half of the year,  we round the year number up by 1
            lease_duration_left = lease_end_year - current_year
            df.at[index,'remaining_lease'] = lease_duration_left
        
        if "TO" in row["storey_range"]:
            # convert storey_range from e.g. 3 TO 5 to e.g. 4
            storey_range_min_max = row["storey_range"].split("TO")
            mid_floor_value = middle_floor_value(storey_range_min_max[0], storey_range_min_max[1])
            df.at[index,'storey_range'] = mid_floor_value
            
        
    # now that month has been used to calculate remaining lease, we convert the month into a format that the 
    # regression model understands
    df['month'] = pd.to_datetime(df['month'])
    df['month'] = df['month'].map(datetime.toordinal)
    print(f"Data processing done in {(datetime.now() - initial_time).total_seconds()}")

    columns_to_remove = ['street_name', 'block']
    result = remove_columns(df, columns_to_remove)

    return result


def get_category_encoder_mapping(encoder, df):
    """Function to produce a dictionary with the format { column_name : {unique_value : binary_encoding_list } }.
    Requires original encoder (which should contain all encoded values) and the original dataset as a dataframe (to extract all unique values of a column)"""
    encoder_params = encoder.get_params()
    output_dict = {}
    for col_name in encoder_params["cols"]:
        unique_values = df[col_name].unique()
        mapping_df = [m["mapping"] for m in encoder_params["mapping"] if m['col'] == col_name][0]
    
        value_to_encoded = {}
        counter = 0
        for value in unique_values:
            value_to_encoded[value] = mapping_df.iloc[counter].values.tolist()
            counter += 1
        output_dict[col_name] = value_to_encoded
    return output_dict


def categorise_ml_data(df, encoder_mapping = None):
    """Convert columns with categorical data (e.g. town, flat type) """
        
    # encode categorical data: town, flat type and flat model
    initial_time = datetime.now()

    # either binary or base-n, depending on how many extra columns you need to show categorical data
    if not encoder_mapping:
        print("CATEGORY ENCODERS EMPTY. GENERATING NEW")
        # encoder = {}
        encode_columns = ['town', 'flat_type', 'flat_model']
        category_encoder = ce.BinaryEncoder(cols=encode_columns)
        
        transformed_df = category_encoder.fit_transform(df)
        encoder_mapping = get_category_encoder_mapping(category_encoder, df)
        print(encoder_mapping)
        # encoder = get_category_encoder_mapping()

        # ce_town = ce.BinaryEncoder(cols=['town']) 
        # ce_flat_type = ce.BinaryEncoder(cols=['flat_type']) 
        # ce_flat_model = ce.BinaryEncoder(cols=['flat_model'])
    else:
        print("ENCODER MAPPINGS EXIST, DETAILS BELOW.")
        print(encoder_mapping)

        for col in encoder_mapping: # for each column i have to manually encode
            value_to_change = df.iloc[0][col]
            print(f"Column: {col}\nValue to change: {value_to_change}\nEncoded value: {encoder_mapping[col][value_to_change]}")
            counter = 0
            # index_target = df.columns.get_loc(col) # for each encode column to store binary numbers i have to add
            for encoder_column in encoder_mapping[col][value_to_change]:
                df.insert(df.columns.get_loc(col), f'{col}_{counter}', encoder_column)
                counter += 1
            df = df.drop(columns=[col])  # remove original column
        transformed_df = df
    # for en in ce_list:
    #         print(en.get_params())

    print(f"Categorical data conversion done in {(datetime.now() - initial_time).total_seconds()}")

    return {"dataframe" : transformed_df, "encoder_mapping" : encoder_mapping}





# def clean_data(df, encoder_list):
#     """Processes data (standardising data format, removing columns deemed unnecessary 
#     and converting categorical data into numbers for regression model.
#     Returns both the cleaned data and a dictionary containing all category encoders used."""
#     df = process_ml_data(df)
#     columns_to_remove = ['street_name', 'block']
#     result = categorise_ml_data(remove_columns(df, columns_to_remove), encoder_list)
#     return result


class ML_Model:

    def __init__(self):
        """Produce the trained ML model"""
        print("Initialising connection to database")
        db_obj = get_db()
        initial_time = datetime.now()
        cursor = db_obj.find({"month": {"$gte": "2017-01"}}, projection={'_id': False})
        print(f"Query done in {(datetime.now() - initial_time).total_seconds()}")
        print("Next")
        counting = 1
        
        # for e in cursor:
        #     print(counting)
        #     counting += 1
            
        result = dumps(cursor)
        print("Dump done")
        print(result[:100])
        result = json.loads(result)
        print(type(result))
        initial_time = datetime.now()
        # result = clean_data(pd.DataFrame(result), None)
        print("Processing data")
        result = process_ml_data(pd.DataFrame(result))
        result = categorise_ml_data(result, None)
        print(f"Result processed in {(datetime.now() - initial_time).total_seconds()}")
        df = result["dataframe"]
        self.encoder_mapping = result["encoder_mapping"]

        cols = list(df.columns.values) #Make a list of all of the columns in the df
        cols.pop(cols.index('resale_price'))
        df = df[cols+['resale_price']] #Create new dataframe with columns in the order you want


        x = df.iloc[:,0:-1]  # contains all independent variables required for the model to derive the resale price
        y = df.iloc[:,-1] # series object containing all resale price data

        x.info()
        print(x.head(3))
        y.info()

        initial_time = datetime.now()
        # x_train, x_test, y_train, y_test=train_test_split(x, y, test_size=0.3)
        poly_features = preprocessing.PolynomialFeatures(degree=3)
        x_poly = poly_features.fit_transform(x)

        x_train,x_test,y_train,y_test = train_test_split(x_poly,y,test_size=0.4)

        polynomial_regression = LinearRegression(fit_intercept=True, n_jobs=1, normalize=False)

        polynomial_regression.fit(x_train,y_train) # fit sample values to sample answers
        
        predicted_result = polynomial_regression.predict(x_test)
        print("MSE: ",np.sqrt(mean_squared_error(y_test,predicted_result)))
        print("R2: ",r2_score(y_test,predicted_result))
        print("RMSE: ",polynomial_regression.score(x_test,y_test))
        print(f"Model trained and evaluated in {(datetime.now() - initial_time).total_seconds()}")
        
        self.model = polynomial_regression

    def predict_values(self, df):
        # processed_df = clean_data(df, self.encoder_list)["dataframe"]

        result = process_ml_data(pd.DataFrame(df))
        processed_df = categorise_ml_data(result, self.encoder_mapping)["dataframe"]
        print(processed_df)

        print(processed_df.head(3))
        poly_features = preprocessing.PolynomialFeatures(degree=3)
        df_poly = poly_features.fit_transform(processed_df)
        print(df_poly.view())
        
        return self.model.predict(df_poly)



if __name__ == "__main__":
    e = ML_Model()
    


    
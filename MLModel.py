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

def process_ml_data(df):
    """Helper function, fills up null values, standardises column data"""
    middle_floor_value = lambda min_floor_str, max_floor_str : int((int(max_floor_str) + int(min_floor_str)) / 2)
    initial_time = datetime.now()
    for index, row in df.iterrows():
        
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

    return df


def categorise_ml_data(df, ce_list = None):
    """Convert columns with categorical data (e.g. town, flat type) """
        
    # encode categorical data: town, flat type and flat model
    initial_time = datetime.now()

    # either binary or base-n, depending on how many extra columns you need to show categorical data
    if not ce_list:
        print("CATEGORY ENCODERS EMPTY. GENERATING NEW")
        ce_list = []
        encode_columns = ['town', 'flat_type', 'flat_model']
        for col in encode_columns:
            ce_list.append(ce.BinaryEncoder(cols=[col]))

        # ce_town = ce.BinaryEncoder(cols=['town']) 
        # ce_flat_type = ce.BinaryEncoder(cols=['flat_type']) 
        # ce_flat_model = ce.BinaryEncoder(cols=['flat_model'])
    else:
        print("CATEGORY ENCODERS EXIST, DETAILS BELOW.")
        for en in ce_list:
            print(en.get_params())

    
    for category_encoder in ce_list:
        df = category_encoder.fit_transform(df)
    
    for en in ce_list:
            print(en.get_params())

    print(f"Categorical data conversion done in {(datetime.now() - initial_time).total_seconds()}")

    return {"dataframe" : df, 
    "encoder_list" : ce_list}


def remove_columns(df, column_name_list):

    for col in column_name_list:
        if col in df.columns:
            df = df.drop(col, axis=1)
        else:
            print(f"'{col}' column not found. skipping...")
    return df


def clean_data(df, encoder_list):
    """Processes data (standardising data format, removing columns deemed unnecessary 
    and converting categorical data into numbers for regression model.
    Returns both the cleaned data and a dictionary containing all category encoders used."""
    df = process_ml_data(df)
    columns_to_remove = ['street_name', 'block']
    result = categorise_ml_data(remove_columns(df, columns_to_remove), encoder_list)
    return result


class ML_Model:

    def __init__(self):
        """Produce the trained ML model"""
        print("Initialising connection to database")
        db_obj = get_db()
        initial_time = datetime.now()
        cursor = db_obj.find({}, projection={'_id': False})
        print(f"Query done in {(datetime.now() - initial_time).total_seconds()}")
        result = json.loads(dumps(cursor))

        result = clean_data(pd.DataFrame(result), None)
        df = result["dataframe"]
        self.encoder_list = result["encoder_list"]

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
        for en in self.encoder_list:
            print(en.get_params())
        self.model = polynomial_regression

    def predict_values(self, df):
        processed_df = clean_data(df, self.encoder_list)["dataframe"]

        print(processed_df.head(3))
        poly_features = preprocessing.PolynomialFeatures(degree=3)
        df_poly = poly_features.fit_transform(processed_df)
        print(df_poly.view())
        
        return self.model.predict(df_poly)



if __name__ == "__main__":
    e = ML_Model()
    


    
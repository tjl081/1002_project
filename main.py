import eel
import pandas as pd
import json
import glob
import os


def pd_to_json(df):
    """helper function, converts python dataframe to json-formatted string"""
    result = df.to_json(orient="index")
    parsed = json.loads(result)
    return parsed

def get_csv_as_pd():
    """helper function, converts all data rows in all csv files in the "data" folder into a single python dataframe"""
    path = os.getcwd() + '\\data\\cleaned\\'
    print(f"CWD:{path}")
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    df = pd.concat((pd.read_csv(f) for f in csv_files), ignore_index=True)
    return df

@eel.expose
def say_hello_py(x):
    print('Hello from %s' % x)

@eel.expose
def test_df():
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)
    return pd_to_json(df)

@eel.expose
def get_dropdown_values(input_df = None, column_names = []):
    """retrieves all unique data from specified columns in the .csv file containing dataset"""
    output_dict = {}
    if len(column_names) > 0:

        if input_df == None:
            input_df = get_csv_as_pd()

        for name in column_names:
            if name in input_df.columns:
                output_dict[name] = list(input_df[name].unique())
            else:
                print(f"{name} is not a valid column.\n Column list:{input_df.columns}\n")
        return json.loads(json.dumps(output_dict, indent = 4))
    else:
        print("No columns specified in function. Aborting....")
        return None
         

@eel.expose
def query_csv(search_query_json = None, max_rows = 2000):
    """retrieves data from .csv file containing dataset. returns data as JSON to allow the Javascript code to handle the data as an object"""
    df = get_csv_as_pd()

    if search_query_json: # if there is a JSON object added into the parameters
        # https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/ for multiple query method
        search_query_dict = json.load(search_query_json)
        # sample search_query_json = {
        #     "month": "",
        #     "town": "",
        #     "flat_type": "",
        #     "street_name": "",
        #     "storey_range": "",
        #     "floor_area_sqm": "",
        #     "flat_model": "",
        #     "lease_commencement_date": "",
        #     "resale_price": "",
        #     "remaining_lease": ""
        # }

    df = df.iloc[:max_rows]  # determines max rows shown
    return pd_to_json(df)




if __name__ == "__main__":
    
    eel.init('web', allowed_extensions=['.js', '.html'])
    # mode value depends on preferred browser. should find a way to implement our own browser check
    print("main.py running") 
    say_hello_py('Python World!')
    eel.say_hello_js('Python World!2')   # Call a Javascript function. the results are queued then displayed the moment the webpage starts up
    eel.start('main.html', mode="chrome-app") # code seems to pause here while website is running.




# we constantly fetch data from the CSV with every user query. while this seems inefficient, it is the only way (i know) to get live data.
# also easier integration when converting to database access


# find a way (e.g. flexbox) to arrange the search fields, before anything else
# then u use the existing input fields to test queries
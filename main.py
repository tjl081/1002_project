import eel
import pandas as pd
import json
import glob
import os


def pd_to_json(df):
    result = df.to_json(orient="index")
    parsed = json.loads(result)
    return parsed

@eel.expose
def say_hello_py(x):
    print('Hello from %s' % x)

@eel.expose
def test_df():
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)
    return pd_to_json(df)

@eel.expose
def query_csv():
    path = os.getcwd() + '\\data\\'
    print(f"CWD:{path}")
    csv_files = glob.glob(os.path.join(path, "*.csv"))

    df = pd.concat((pd.read_csv(f) for f in csv_files), ignore_index=True)
    df = df.iloc[:2000]  # determines max rows shown
    return pd_to_json(df)




if __name__ == "__main__":
    
    eel.init('web', allowed_extensions=['.js', '.html'])
    # mode value depends on preferred browser. should find a way to implement our own browser check
    print("main.py running") 
    say_hello_py('Python World!')
    eel.say_hello_js('Python World!2')   # Call a Javascript function. the results are queued then displayed the moment the webpage starts up
    eel.start('main.html', mode="chrome-app") # code seems to pause here while website is running.


# current decided flow: javascript will have the main code thread
# the javascript will constantly query the python to retrieve DF data.
# if we do not want to use python global variable, we can just store the DF as a JSON on the javascript side
import os
import pandas as pd
import glob



if __name__ == "__main__":
    path = os.getcwd() + '\\data\\'
    print(f"CWD:{path}")
    csv_files = glob.glob(os.path.join(path, "*.csv"))       

    print("Loading csv data to dataframe...")
    df = pd.concat((pd.read_csv(f) for f in csv_files), ignore_index=True)

    print("Data standardising...")
    df.loc[df['flat_type'] == "MULTI GENERATION", 'flat_type'] = "MULTI-GENERATION"
    df['flat_model'] = df['flat_model'].str.upper()
    
    print("Filling in null values...")
    for index, row in df.iterrows():
        if pd.isnull(row['remaining_lease']):
            # take lease commence date + 99 years, then take the result year and deduct by current year
            lease_end_year  = int(row["lease_commence_date"]) + 99
            year_month_pair = row["month"].split("-")
            current_year = int(year_month_pair[0]) + int(int(year_month_pair[1]) > 7) # if the current date is 2nd half of the year,  we round the year number up by 1
            lease_duration_left = lease_end_year - current_year
            df.at[index,'remaining_lease'] = lease_duration_left
    
    
    print("Done. Exporting data....")
    os.makedirs(path + '\\cleaned', exist_ok=True)  
    df.to_csv(path + '\\cleaned\\clean.csv', index=False)  
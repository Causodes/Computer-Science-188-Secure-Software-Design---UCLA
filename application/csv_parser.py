import pandas as pd

# import date from csv file
# file must be in same directory, otherwise include path as well
# template by column: url, username, password
def read_csv(filename):
    data = pd.read_csv(filename)
    for index, row in data.iterrows():
        if not (row[0] and row[1] and row[2]):
            print("Error: missing data field for entry number " + str(index + 1))
            continue
        url, username, password = row
        """
        Add code here to incorporate data to password vault
        """

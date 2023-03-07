import pandas as pd
from sqlalchemy import create_engine
import os

def getPaths(directory,extension):
    paths = filter(lambda path:path.find(extension)!=-1,os.listdir(directory))
    paths = map(lambda path:os.path.join(directory, path),paths)
    return list(paths)

def getTableName(bus):
    return 'ae%s' % f'{bus:02d}'

SERVER='128.200.20.247,40247'
DB='BEB'
USER='rfh'
PASSWORD='cvptemo256325'

# Create a connection string to connect to SQL Server
conn_str = f'mssql+pymssql://{USER}:{PASSWORD}@{SERVER}/{DB}'

path = getPaths('.\\data','.csv')[0]
table = getTableName(1)

# Read the CSV file into a pandas dataframe
df = pd.read_csv(path)

# Use the pandas to_sql() function to push the dataframe to SQL Server
engine = create_engine(conn_str)
df.to_sql(name=table, con=engine, if_exists='replace', index=False)

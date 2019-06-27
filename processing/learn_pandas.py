import pandas as pd

df = pd.read_csv('raw_sync_data_27-06-2019(14_29).csv')

# print("\nPrint n rows from head and dowwards:")
# print(df.head(51))
#
# print("\nPrint all column names:")
# print(df.columns)
#
# print("\nPrint specified amount of lines:")
# print(df.iloc[1:4])
#
# print("\nPrint specific location:\n" + df.iloc[1,1])
#
# print("\nIterate through rows:")
# for i, row in df.iterrows():
#     print(str(i) + "\t" + str(row))
#
# print(df.loc[df['Node'] == "10.0.0.11"])

# print(df.sort_values(['Event_ID', 'Node'], ascending=[1,1]))
print(df.Node.unique())
import pandas as pd

TIMER_MAX_VAL = 1000000

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
#
# print(df.sort_values(['Event_ID', 'Node'], ascending=[1,1]))

# print("\nFind each unique entry in a column:")
# print(df.Node.unique())


df_init = {'Sample #':[], 'RT Clock':[], 'Max timestamp delta in microseconds':[]}
df_nice = pd.DataFrame(df_init)

# print(df_nice)

# Get all unique node names and add a new column for each in the data frame
nodes = df.Node.unique()
nodes.sort()
for node_id in nodes:
    df_nice[node_id] = 'default value'

# Get all unique samples and assign one row for each in the data frame
sample_ids = df.Event_ID.unique()
sample_ids.sort()
for i in sample_ids:

    y = {'Sample #': i}
    x = df.loc[df['Event_ID'] == i]
    y.update({'RT Clock': x.iloc[0]['Local_time']})

    timestamp_list = []
    timestamp_diff = []

    for j, row in x.iterrows():
        y.update({row.Node: row.Timestamp})
        timestamp_list.append(row.Timestamp)

    for j in timestamp_list:
        for k in timestamp_list:
            diff = abs(j - k)
            if diff > TIMER_MAX_VAL/2:
                diff = TIMER_MAX_VAL - diff
            timestamp_diff.append(diff)

    y.update({'Max timestamp delta in microseconds': max(timestamp_diff)})




    print(timestamp_list)
    df_nice = df_nice.append(y, ignore_index=True)

df_nice['Sample #'] = df_nice['Sample #'].astype(int)
df_nice['Max timestamp delta in microseconds'] = df_nice['Max timestamp delta in microseconds'].astype(int)

print(df_nice)
df_nice.to_csv('refined_results.csv')
# for i in sample_ids:
#     df_nice = df_nice.append({'Sample #': i}, ignore_index=True)
# print(df_nice)

# Iterate through the entire raw dataset and transfer data to the refined dataset
# for i, row in df.iterrows():
#     print(row.Event_ID)

#
# print(df_nice['Event_ID' == 1].index[0])

# x = df.loc[df['Event_ID'] == 2]
# for i, row in x.iterrows():
#     print(row.Event_ID)
# print(x)


#
# a = {'ting': 1}
# b = {'tang': 1}
#
# a.update(b)
#
# print(a)
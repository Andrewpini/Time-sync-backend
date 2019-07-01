import pandas as pd

TIMER_MAX_VAL = 10

df = pd.read_csv('raw_sync_data_27-06-2019(14_29).csv')

df_init = {'Sample #': [], 'RT Clock': [], 'Max timestamp delta in microseconds': []}
df_nice = pd.DataFrame(df_init)

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
    df_nice = df_nice.append(y, ignore_index=True)

df_nice['Sample #'] = df_nice['Sample #'].astype(int)
df_nice['Max timestamp delta in microseconds'] = df_nice['Max timestamp delta in microseconds'].astype(int)

df_nice.to_csv('refined_results.csv')

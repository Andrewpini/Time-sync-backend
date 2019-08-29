import numpy as np
import pandas as pd
import random

# arrays = [np.array(['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux']), np.array(['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two'])]
# print(arrays)
#
# df = pd.DataFrame(np.random.randn(8, 4), index=arrays)
# df = df.transpose()
# df.to_csv('nosse.csv', index=arrays)



df_init = {'Sample #': [], 'RT Clock': [], 'Max timestamp delta in microseconds': []}
df_nice = pd.DataFrame(df_init)

new = {'Sample #': 1, 'RT Clock': '22.13.59', 'Max timestamp delta in microseconds': 3}
new.update({'Knast': 000})
new2 = {'Sample #': 0, 'RT Clock': '22.13.59', 'Max timestamp delta in microseconds': 6, 'nisse': 321}
df_nice = df_nice.append(new, ignore_index=True)
df_nice = df_nice.append(new2, ignore_index=True)


# df_nice['nisse'] = ''

df_nice.to_csv('pandas_csv.csv')

# x = pd.DataFrame()
# x = pd.DataFrame({'instance':['first','first','first'],'foo':['a','b','c'],'bar': 1})
# x = x.set_index(['instance','foo']).transpose()
#
# idx = pd.MultiIndex.fr[(u'first', u'a'), (u'first', u'b'), (u'first', u'c')]
#
# x.to_csv('pandas_csv.csv')
# x.to_csv('pandas_csv2.csv', index=idx)
#


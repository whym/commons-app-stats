#!/usr/bin/env python
'''
TODO: transform this to one-off script that generates stats for last 30days (no merging)
'''
import os
import sys
import oursql
import pandas as pd
import argparse

cas_file = os.path.expanduser('~/data/r01.json')

def main(limit):
    conn = oursql.connect(host = 'commonswiki.labsdb',
                          read_default_file=os.path.expanduser('~/.my.cnf'),
                          db = 'commonswiki_p',
                          use_unicode=False)
    command = '''
SELECT *
FROM recentchanges
WHERE rc_comment LIKE "%using Android Commons%" OR rc_comment LIKE "%Via Commons Mobile App%"
ORDER BY rc_timestamp DESC
LIMIT ''' + str(limit)
    df = pd.read_sql(command, conn).set_index('rc_id')

    # extract data we want to see
    df['cas_version'] = '0.1'
    df['cas_date'] = df.rc_timestamp
    df['cas_action'] = 'unknown'
    df.loc[(df.rc_type == 0, 'cas_action')] = 'edit' 
    df.loc[((df.rc_type == 3) & (df.rc_log_type == b'upload'), 'cas_action')] = 'upload' 

    # save this 
    filename = 'data/seq/r01_%s_%d_l%d.pickle' % (df.iloc[0].rc_timestamp.decode('utf8'), df.index[0], limit)
    df.to_pickle(filename)

    # merge into the main file
    dfm = pd.DataFrame()
    if os.path.exists(cas_file):
        dfm = pd.read_json(cas_file)
    df = df.append(dfm)
    print('%d entries, %d duplicates' % (len(df), len(df[df.index.duplicated()])))
    df = df[~ df.index.duplicated()]
    df.to_json(cas_file, orient='records')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int,
                        default=10000)
    options = parser.parse_args()
    main(options.limit)

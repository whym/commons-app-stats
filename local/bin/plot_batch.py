#!/usr/bin/env python
'''

'''
import os
import sys
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine, text
import pandas as pd
import argparse
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime
from os.path import expanduser
from random import randint


COL_ACT  = 'action'
COL_DATE = 'date'
COL_USER = 'user'
COL_TITLE = 'title'


def retrieve_logged_actions(conn, start, end):
    command = text('''
SELECT /* SLOW_OK */ *
FROM logging LEFT JOIN page ON log_namespace = page_namespace AND log_title = page_title
WHERE (log_comment LIKE "%using Android Commons%" OR log_comment LIKE "%Via Commons Mobile App%" OR log_comment LIKE "%COM:MOA\\|Commons%")
AND log_timestamp > "{start}" AND log_timestamp < "{end}"
ORDER BY log_timestamp DESC
'''.format(start=start, end=end))
    df = pd.read_sql(command, conn)

    # extract data we want to see
    df[COL_DATE] = pd.to_datetime(df.log_timestamp.str.decode('utf-8'))
    df[COL_ACT] = '?. upload (?)'
    df[COL_USER] = df.log_user_text.str.decode('utf-8')
    df[COL_TITLE] = df.log_title.str.decode('utf-8')
    df.loc[(df.log_action == b'overwrite', COL_ACT)] = '2. upload (overwriting)'
    df.loc[(df.log_action == b'upload', COL_ACT)] = '1. upload (new)'
    df.loc[(pd.isnull(df.page_id), COL_ACT)] = '3. upload (deleted)'
    return df


def retrieve_edits(conn, start, end):
    command = text('''
SELECT /* SLOW_OK */ *
FROM revision JOIN page ON rev_page = page_id
WHERE (rev_comment LIKE "%using Android Commons%" OR rev_comment LIKE "%Via Commons Mobile App%" OR rev_comment LIKE "%COM:MOA\\|Commons%")
AND rev_timestamp > "{start}" AND rev_timestamp < "{end}"
ORDER BY rev_timestamp DESC
'''.format(start=start, end=end))
    df = pd.read_sql(command, conn)

    # extract data we want to see
    df[COL_DATE] = pd.to_datetime(df.rev_timestamp.str.decode('utf-8'))
    df[COL_ACT] = '?. edit (?)'
    df[COL_USER] = df.rev_user_text.str.decode('utf-8')
    df[COL_TITLE] = df.page_title.str.decode('utf-8')
    df.loc[(df.rev_parent_id != 0, COL_ACT)] = '5. edit (modifying)'
    df.loc[(df.rev_parent_id == 0, COL_ACT)] = '4. edit (new)'
    return df


def aggregate(df, sampling):
    print(df[COL_ACT].value_counts())
    # skip new page creation - it duplicates new upload
    df = df[df[COL_ACT] != '4. edit (new)']

    samples = df[[COL_ACT]].groupby(COL_ACT).resample(sampling).apply(len).unstack(COL_ACT, fill_value=0)
    #samples.columns = samples.columns.droplevel()
    print(samples)
    return samples


def plot_stacked_bar_chart(labels, samples, file_name, title):
    fig, ax = plt.subplots(figsize=(10,6))

    samples.plot.bar(stacked=True, ax=ax, ec=(0.1, 0.1, 0.1, 0.7), alpha=0.7)
    #samples.plot.bar(stacked=True, ax=ax, ec=(0.1, 0.1, 0.1, 0.7), alpha=0.7, color=['blue', 'green', 'red', 'black'])
    ax.grid(True)
    ax.set_axisbelow(True)
    gridlines = ax.get_xgridlines() + ax.get_ygridlines()
    for line in gridlines:
        line.set_linestyle('--')

    ax.legend(loc=2, fontsize=10, fancybox=True).get_frame().set_alpha(0.7)
    ax.set_xticklabels(labels)
    ax.set_xlabel('')
    fig.autofmt_xdate()
    plt.title(title)
    fig.savefig(file_name)


def collect_data(options):
    url = URL(
        drivername='mysql.mysqldb',
        host='commonswiki.analytics.db.svc.eqiad.wmflabs',
        database='commonswiki_p',
        query={ 'read_default_file' : os.path.expanduser('~/.my.cnf'),
                'use_unicode': 0 }
    )
    conn = create_engine(url)

    start = format_ts(options.start)
    end = format_ts(options.end)
    actions = retrieve_logged_actions(conn, start, end)
    edits   = retrieve_edits(conn, start, end)
    df = actions[[COL_DATE, COL_ACT, COL_USER, COL_TITLE]].append(edits[[COL_DATE, COL_ACT, COL_USER, COL_TITLE]])
    return df


def format_ts(d):
    return '{:04d}{:02d}{:02d}'.format(d.year, d.month, d.day)


def random_date(start, end):
    return start + pd.Timedelta(
        seconds=randint(0, int((end - start).total_seconds())))


def generate_dummy_data(options):
    actions = ['upload (dummy)'] * 20 + ['edit (dummy)'] * 15 + ['misc']
    users = ['NoName'] * len(actions)
    titles = ['NoTitle'] * len(actions)
    df = pd.DataFrame([[random_date(options.start, options.end),
                        actions[randint(0, len(actions)-1)],
                        users, titles] for x in range(0, 2000)],
                      columns=[COL_DATE, COL_ACT, COL_USER, COL_TITLE]).reindex()
    return df


def main(options):
    try:
        df = collect_data(options)
    except Exception as e:
        sys.stderr.write("Exception: {}\n".format(e))
        df = generate_dummy_data(options)
    df = df.set_index(COL_DATE)
    samples = aggregate(df, options.sampling)
    labels = samples.index.date.tolist()
    if options.sampling == 'Q':
        labels = ['%dQ%d' % x for x in zip(samples.index.year.tolist(), samples.index.quarter.tolist())]
    elif options.sampling == 'W':
        labels = ['W%d (-%s)' % x for x in zip(samples.index.week.tolist(), samples.index.date.tolist())]
    plot_stacked_bar_chart(
        labels,
        samples,
        expanduser(options.output),
        'Edits and actions made via Commons Android App (per %s)' % options.sampling)
    df.to_csv(options.dump, encoding='utf-8', compression='gzip')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sampling', type=str,
                        default='Y')
    parser.add_argument('--end', type=pd.to_datetime,
                        default='2100')
    parser.add_argument('--start', type=pd.to_datetime,
                        default='1900')
    parser.add_argument('--dump', type=str,
                        default='~/public_html/latest.csv.gz')
    parser.add_argument('--output', type=str,
                        default='~/public_html/latest.png')
    options = parser.parse_args()
    main(options)


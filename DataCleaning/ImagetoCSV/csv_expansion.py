#!/usr/local/bin/python3.6

import pandas as pd
import re

df = pd.read_csv('~/Downloads/bloc_txt.csv', index_col=0)

ids = df.index.values


def get_info(cell):
    txt = [x for x in cell.split('\n') if x.strip() != '']
    info_dict = {'phone': '', 'email': '', 'city_state_zip': '', 'company': '',
                 'attn': '', 'esq': '', 'final_address': ''}
    company_address = []
    esq = []

    for line_raw in txt:
        line = re.sub(r'(?<=\d)\s+(?=\d)', '', line_raw)
        line = line.strip()
        if re.search(r'@', line):
            info_dict['email'] = line
        if re.search(r',\s*[A-Z]\s*[A-Z]\s*\d{5}\b', line):
            info_dict['city_state_zip'] = line
        if re.search(r'\d{3}-\d{3}-\d{4}', line.replace(' ', '')):
            info_dict['phone'] = line
        elif re.search(r'\d{10}', line.replace(' ', '')):
            info_dict['phone'] = line
        elif re.search(r'(\d{3}) \d{3}-\d{4}', line.replace(' ', '')):
            info_dict['phone'] = line
        elif re.search(r'\d{3}-\d{3}-\d{3}', line.replace(' ', '')):
            info_dict['phone'] = line
        r = re.search(r'(.*?)(ATTN.*)', line)
        if r:
            info_dict['attn'] = r.group(2)
            company_address.append(r.group(1))
        if re.search(r'E\s*S\s*Q', line):
            esq.append(line)

        company_address.append(line)
    info_dict['esq'] = '\n'.join(esq)
    f_address = '\n'.join(company_address)
    pattern = re.compile(r'^(\d+)\b', re.M)
    r = re.search(pattern, f_address)
    if r:
        pattern = r'^(.*?)('+r.group(1)+r'.*)'
        r1 = re.search(pattern, '|'.join(company_address))
        if r1:
            info_dict['company'] = r1.group(1).replace('|', '\n').strip()
            info_dict['final_address'] = r1.group(2).replace('|', ' ')
    else:
        info_dict['company'] = '?'
        info_dict['final_address'] = f_address[0]

    info_dict['company'] = re.sub(r'PRESENTER:', '', info_dict['company'])
    info_dict['company'] = re.sub(r'RETURN TO:', '', info_dict['company'])

    addr = info_dict['final_address'].split(' ')
    if info_dict['phone'] in addr:
        addr.pop(addr.index(info_dict['phone']))
    if info_dict['email'] in addr:
        addr.pop(addr.index(info_dict['email']))
    if info_dict['attn'] in addr:
        addr.pop(addr.index[info_dict['attn']])

    zip_index = [x.strip() for x in info_dict['city_state_zip'].split(',')]
    splitter = zip_index.pop().split(' ')
    zip_index = zip_index + splitter
    zip = zip_index[-1]

    if zip in addr:
        addr = addr[:addr.index(zip) + 1]

    info_dict['final_address'] = ' '.join(addr)
    info_dict['company'] = info_dict['company'].strip()
    return info_dict


df_p = pd.DataFrame.from_records(df[df.columns[0]].apply(get_info))
df_p.columns = [['p_{}'.format(x) for x in df_p.columns]]

df_r = pd.DataFrame.from_records(df[df.columns[1]].apply(get_info))
df_r.columns = [['r_{}'.format(x) for x in df_r.columns]]

df = df_p.merge(df_r, left_index=True, right_index=True)

df['ID'] = ids

df.to_csv('/Users/payaj/Downloads/expanded_txt.csv')

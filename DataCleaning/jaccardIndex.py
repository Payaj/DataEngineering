import numpy as np
import pandas as pd
import re
import math

##################################################### #1. This section creates the bigrams of the names. These bigrams will be the input of the jeccard index formula/function ####################################################################
################################## For example if we want to match "Morgan" and "Morgana", this function will convert them into respective bigrams: "['Mo', 'or', 'rg', 'ga', 'an']" and "['Mo', 'or', 'rg', 'ga', 'an', 'na']"#####################
####################################################################### Also this function excludes the middle name in the bigram, just take first and last name into account ######################################################################

def get_bigram_1(text):
    bi_list = []
    u_text = text.split(' ')
    i = text.replace(' ', '')

    temp = []
    for j in u_text:
        #         print(j)
        if len(j) > 0:
            temp.append(j)
    # below line removes the middle name from the name for bigram
    if len(temp) == 3:
        i = temp[0] + temp[2]

    if len(i) >= 2:
        for j in range(len(i) - 1):
            bi_list.append(i[j:j + 2])
    return bi_list

##################################################### #2. This section is the jaccard index formula (Intersection of Two names / Union of two strings) that matches two names and provide them a match score #######################################
#################################### For the above example the intersection will be: "['Mo', 'an', 'ga', 'or', 'rg']" (length = 5), and union will be "['Mo', 'an', 'ga', 'na', 'or', 'rg']" (length = 6) ##########################################
######################################################## According to the jeccard index formula, match will be 5/6 (Intersection of Two names / Union of two strings) = 0.833 ######################################################################

def compute_jaccard_index(set_1, set_2):
    domin = float(len(np.union1d(set_1,set_2)))
    if domin == 0:
        return -1
    return len(np.intersect1d(set_1,set_2)) / domin

####################################################################################################################################################################################################################################################
########################################### #3. This section reads the input file and filter out all the edge cases from the data (such as: name with 4 words, emails, numbers, name with duplicate words in it) ###################################
####################################################################################################################################################################################################################################################

# Below line reads the file
df = pd.read_csv('Jaguar_AgentAndCompany.csv')

# Below line rename the column to Name and CompanyCode
# For this code, SellersCompanyCode is taken into account, can get results from SellersCompany
df.columns = ['Name', 'CompanyCode']

# Below line deletes null rows and columns from the table
df_d = df.dropna()

# Below line remove duplicate rows.
df_d.drop_duplicates(inplace=True)

# Below line converts name in lower case
df_d['Name'] = df_d['Name'].apply(lambda x: x.lower())

# Below line removes all the email addresses from the name column by used '@' as an identifier for the emails.
df_d = df_d[df_d['Name'].apply(lambda x: '@' in x)==False]

# keep [A-Za-z\s] only
# Below line uses regular expression to filter out the names with numbers in them (like 310 gallery)
df_d['Name_for_jac'] = df_d['Name'].apply(lambda x: re.sub('[^A-Za-z\s]',' ',string=x))


# Below function filter out the names with more then 3 words in them, and less than 2 (so a name can have at least 2 words and max. 3)
def filter_name(line):
    k = 0
    for i in line.split(' '):
        if len(i)>=2:
            k+=1
    if len(line.split(' ')) != len(set(line.split(' '))):
        return False
    return 1<k<4

# Below function uses the above "filter_name" function
df_d = df_d[df_d['Name_for_jac'].apply(filter_name)]

# Below function creates column for bigram in the dataset by using "get_bigram_1" from Section 1
df_d['Name_bigram'] = df_d['Name_for_jac'].apply(get_bigram_1)

# Below code creates a list of names by company.

companies = df_d['CompanyCode'].unique()
dfs = []
for i in companies:
    dfs.append(df_d[df_d['CompanyCode']==i])

####################################### #4. This section calls the "Section 1" (Jaccard Index formula) for all the Agents of same company, and if two names have differernt initials, it divides the jaccard match by 2 ###############################

def get_jaccard_list(df1, dict_list):
    count = 0

    # i is the index of one name, which will be matched with all the other names of the same company (with index j - next for loop)
    for i in df1.index:
        count += 1
        if count % 10 == 0:
            print(count)
        k = 0
        max_index = [i]
        for j in df1.index:
            if i == j:
                continue
            tmp = compute_jaccard_index(df1.loc[i, 'Name_bigram'], df1.loc[j, 'Name_bigram'])

            # i1 and i2 are the first name and last name initials of the name with index i
            i1 = df1.loc[i, 'Name_for_jac'].split()[0][0]
            i2 = df1.loc[i, 'Name_for_jac'].split()[-1][0]
            # j1 and j2 are the first name and last name initials of the name with index j
            j1 = df1.loc[j, 'Name_for_jac'].split()[0][0]
            j2 = df1.loc[j, 'Name_for_jac'].split()[-1][0]

            # if both names and different initials, the tmp (jeccard match score will be divided by 2)
            if i1 != j1 or i2 != j2:
                tmp = tmp / 2

            # here we are only saving the index of the match score in "max_index", if the new match score (tmp) is greater than the previous match score.
            if tmp > k:
                max_index = [j]
                k = tmp
                continue

            # if there are more names with same match score, below 2 lines will save those match score also
            if tmp == k:
                max_index.append(j)

        # after the completion of one loop of first for loop (index i), the below code saves the index i, max_index (index of the name that was the max. match), and the value of the max. match score (k)
        dict_list.append({'index_1': i, 'index_2': max_index, 'jaccard index': k})

######################################################################## 5. Calling of section 4 (above function), and writing final csv ########################################################
dict_list = []
count = 0
# Below code call the above function (section 4) by inputting agent names of same company.
for df1 in dfs:
    print('dfs number',count, 'start','has:' ,len(df1))
    count +=1
    get_jaccard_list(df1,dict_list)

# below code converts the 'dict_list' (section 4) output into data frame.
df3 = pd.DataFrame.from_records(dict_list)
df_output = df3

# index_2 column in the df_output column can have multiple match, so can have different indexes, below function creates different col. for all those indexes, and then below codes merge the clean data frame with "df_d" by index, and get the right names for the indexes.
def index_clean(line):
    indexs = line['index_2']
    if line['index_1'] == int(indexs[0]):
        return {'index_c0': int(line['index_1'])}
    dict_ = dict([('index_c' + str(i), '') for i in range(len(indexs))])
    for i in range(len(indexs)):
        dict_['index_c' + str(i)] = int(indexs[i])
    return dict_

df_index= pd.DataFrame.from_records(df_output.apply(index_clean, axis=1))


df_output = df_output.merge(right = df_index, how='inner', left_index = True, right_index=True)
df_output.head(10)
df_output = df_output.merge(right = df_d, how='left', left_on='index_1', right_index=True).merge(right = df_d, how='left', left_on='index_c0', right_index=True)

# Below code filter out all the agents with company "STRE" ("EASY RE")
df_output_1 = df_output.loc[df_output['Company_x'].apply(lambda x: not('STRE' in x))]
print len(df_output_1)
"Below code exports the dataframe in a csv"
df_output_1.to_csv("jaccard_index_1005_1.csv")

df_output[['index_1', 'index_2','Name_x','Name_y', 'jaccard index', 'Company_x',
       'Name_for_jac_x', 'Name_bigram_x',
       'Name_for_jac_y', 'Name_bigram_y']].to_csv('output_new.csv')




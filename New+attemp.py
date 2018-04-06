
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import math
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from random import shuffle


# ## Import Dataset

# In[87]:


fulldataset = pd.read_csv("subsdata.csv", delimiter=",")
usagedataset = pd.read_csv("usage.csv", delimiter=",")
db = fulldataset[["MSISDN","INVOICENUMBER","ISCORPTREATMENT","VOICE", "SMS", "DATA", "THISMONTHBILL","DISCOUNT"]]


# ## Convert Float to Int
# The numbers represent usage & money value. No need decimal points.

# In[90]:


db["MSISDN"] = [str(i) for i in db["MSISDN"]]
db["INVOICENUMBER"] = [str(i) for i in db["INVOICENUMBER"]]
db["ISCORPTREATMENT"] = [int(i) for i in db["ISCORPTREATMENT"]]
db["DATA"] = [int(i) for i in db["DATA"]]
db["SMS"] = [int(i) for i in db["SMS"]]
db["VOICE"] = [int(i) for i in db["VOICE"]]
db["THISMONTHBILL"] = [int(i) for i in db["THISMONTHBILL"]]
db["DISCOUNT"] = [int(i) for i in db["DISCOUNT"]]


# ## Getting Correlation Usage --> This Month Bill

# In[91]:


def getcorr(a,b):
    return np.corrcoef(a,b)
print(getcorr(db["VOICE"], db["DISCOUNT"]))
print(getcorr(db["SMS"], db["DISCOUNT"]))
print(getcorr(db["DATA"], db["DISCOUNT"]))


# ## Find Similarity between each data points.

# In[114]:


import numpy as np
db["usage_list"] = [i for i in db.values[:,1:4]]
A = []

index = 1580

for j in range(len(db["usage_list"])):
    if(j != index and db["ISCORPTREATMENT"][j] == 0):
        #distance = math.sqrt(sum([(db["usage_list"][1] - db["usage_list"][2])]))
        distance = euclidean_distances([db["usage_list"][index]], [db["usage_list"][j]])
        A.append((distance, db["THISMONTHBILL"][j], db["INVOICENUMBER"][j], j))
        
A.sort()
closest = A[:10]
closest.sort(key=lambda tup: tup[1])
print(db.values[index])

closest = [i for i in closest if(i[1]<db["THISMONTHBILL"][index])]
closest


# ## Merge the dataset, find correlation between particular item to discount

# In[8]:


merged_left = pd.merge(left = fulldataset, right=usagedataset, how = "left", left_on = "INVOICENUMBER", right_on = "INVOICENUMBER")
mtx = usagedataset["ITEM"] == "DATA"
print(mtx.corr(merged_left["DATACHARGES"]))


# In[41]:


index_of_invoice = [i[2] for i in closest]
all_items = []

user = merged_left["INVOICENUMBER"] == int(db["INVOICENUMBER"][index])
items = merged_left[user].ITEM.tolist()

for i in index_of_invoice:
    all_items.append(merged_left.ITEM.loc[(merged_left["INVOICENUMBER"] == int(i)) & ~merged_left["ITEM"].isin(items)].tolist())

# print(items)
asod = [x for j in all_items for x in j]
list(set(asod))


# ## Correlation ITEMS and Thismonthbill

# In[113]:


dummy_usage = usagedataset
tmp = []
merged_left["ITEM"] = [str(i) for i in merged_left["ITEM"]]
for i in merged_left["ITEM"]:
    #print(i)
    if(i[0:4] == "DATA"):
        i = "Data"
    elif(i[0:11] == "SMS Content"):
        i = "SMS Content"
    elif(i[0:14] == "Super Internet"):
        i = "SuperInternet"
    tmp.append(i)
merged_left["ITEM"] = tmp

Z = merged_left["ITEM"] == "Data"
merged_left[Z]

# z = list(set(merged_left["ITEM"]))
# z.sort()
# q = []
# for i in z:
#     mtx = merged_left["ITEM"] == i
#     Q = mtx.corr(merged_left["THISMONTHBILL"])
#     q.append((Q,i))

# q.sort()
# q


# In[103]:


calling_plan = [i for i in fulldataset["CALLINGPLAN"]]
x = list(set(calling_plan))
x.sort()
q = []
for i in x:
    mtx = fulldataset["CALLINGPLAN"] == i
    Q = mtx.corr(merged_left["MONTHLYFEE"])
    #R = mtx.corr(merged_left["DATA"])
    #T = mtx.corr(merged_left["VOICE"])
    q.append((Q,i))
q.sort()
q


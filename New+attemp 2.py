
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


# ## Import Usage & Subs Dataset

# In[212]:


fulldataset = pd.read_csv("newdataset.csv", delimiter=",")
usagedataset = pd.read_csv("usage_new.csv", delimiter=",")
#converting the data from int to str. [:-2] will get rid the .0 (float decimal)
usagedataset["msisdn"] = ["0"+str(i)[:-2] for i in usagedataset["msisdn"]]
usagedataset["invoicenumber"] = ["0"+str(i)[:-2] for i in usagedataset["invoicenumber"]]
usagedataset["accountnumber"] = ["0"+str(i)[:-2] for i in usagedataset["accountnumber"]]

#setup iscorptreatment == 1
corporate_db = fulldataset.loc[fulldataset["iscorptreatment"] == 1]
corporate_db = corporate_db.reset_index()
del corporate_db["index"]
del corporate_db["iscorptreatment"]
corporate_db["msisdn"] = ["0"+str(i) for i in corporate_db["msisdn"]]
corporate_db["invoicenumber"] = ["0"+str(i) for i in corporate_db["invoicenumber"]]
corporate_db["accountnumber"] = ["0"+str(i) for i in corporate_db["accountnumber"]]

#setup iscorptreatment == 0
private_db = fulldataset.loc[fulldataset["iscorptreatment"] == 0]
private_db = private_db.reset_index()
del private_db["index"]
del private_db["iscorptreatment"]
private_db["msisdn"] = ["0" + str(i) for i in private_db["msisdn"]]
private_db["invoicenumber"] = ["0"+str(i) for i in private_db["invoicenumber"]]
private_db["accountnumber"] = ["0"+str(i) for i in private_db["accountnumber"]]

combine = pd.merge(left = corporate_db, right=usagedataset, how = "left", left_on = "invoicenumber", right_on = "invoicenumber")


# ## Tidying Data

# In[213]:


tmp = []
combine["item"] = [str(i) for i in combine["item"]]
for i in combine["item"]:
    #print(i)
    if(i[0:4] == "DATA"):
        i = "Data"
    elif(i[0:11] == "SMS Content"):
        i = "SMS Content"
    elif(i[0:14] == "Super Internet"):
        i = "SuperInternet"
    tmp.append(i)
combine["item"] = tmp


# ## Getting Probability of occurence of an item
# Save as df--> item & prob

# In[214]:


items = list(set(combine["item"]))
X = []
for i in items:
    counter = 0
    for j in combine.values:        
        if(j[27] == i):
            counter = counter + 1
    X.append((i, counter/len(combine.values)))
df = pd.DataFrame(X)
df.columns = ["item", "probability"]


# ## For every invoicenumber, get their items.
# Save as invoiceitem --> invoicenumber & item

# In[217]:


person = []
for i in corporate_db.values:
    items = []
    for j in combine.values:
        if(i[1] == j[1]):
            items.append(j[27])
    person.append((i[1],items))
invoiceitem = pd.DataFrame(person)
invoiceitem.columns = ["invoicenumber", "item"]


# ## For every invoice number, get their discount.
# Discount would be divided to the thismonthbill in advanced, to get the percentage of them.
# Save as invoicediscount --> invoicenumber & discount

# In[221]:


#Divide the discount with thismonthbill, to get known how much persentage of the discount compare 
x = []
for i in range (len(corporate_db["discount"])):
    if(corporate_db["thismonthbill"][i] != 0):
        tmp = corporate_db["discount"][i]/corporate_db["thismonthbill"][i]
        x.append(tmp*-1)
    else:
        x.append(0)
#x = [((i*-1)-min(x))/(max(x)-(min(x))) for i in x]
  
corporate_db["discount"] = [i for i in x]
invoicediscount = corporate_db[["invoicenumber", "discount"]]


# ## Find Similarity of usage(sms,data,voice) between each data points.
# Using euclidean distance(Usage B - Usage A)
# closest will return a list of 10 closest distance that the bill is cheaper than the targeted input

# In[349]:


corporate_db["usage_list"] = [i for i in corporate_db.values[:,12:15]]
A = []

index = 3

for j in range(len(corporate_db["usage_list"])):
    if(j != index):
        distance = euclidean_distances([corporate_db["usage_list"][index]], [corporate_db["usage_list"][j]])
        A.append((distance, corporate_db["thismonthbill"][j], corporate_db["invoicenumber"][j], j))
        
A.sort()
closest = A[:10]
closest.sort(key=lambda tup: tup[1])
print(corporate_db.values[index])

closest = [i for i in closest if(i[1]<corporate_db["thismonthbill"][index])]
closest


# ## Find Probability of getting discount > its mean.

# In[350]:


itemdiscount = pd.merge(left = invoiceitem, right=invoicediscount, how = "left", left_on = "invoicenumber", right_on = "invoicenumber")
invoice_number = [i[2] for i in closest]
mean = itemdiscount["discount"].mean()
counter = 0
for i in itemdiscount["discount"]:
    if(i>mean):
        counter = counter+1
Pdiscountmean = round((counter/len(itemdiscount["discount"])),5)


# ## Getting The item list from the targeted input & its 10 closest neighboor.
# Targeted_item = targeted input's item list
# all_items = itemlist from 10 closest

# In[355]:


targeted_item = combine.item.loc[combine["invoicenumber"] == corporate_db["invoicenumber"][index]].tolist()
all_items = []
for i in invoice_number:
    for j in itemdiscount.values:
        if(j[0] == i):
            all_items.append(j)

X = []            
for j in all_items:
    mean = itemdiscount["discount"].mean()
    
    for i in targeted_item:
        if((i in j[1]) & (j[2]>mean)):
            X.append((j[0],j[2]))
            print(j[0] + " " +" " + str(j[2]))
            break


# ## From the biggest discount from above, get the invoicenumber.

# In[348]:


print(itemdiscount.item.loc[corporate_db["invoicenumber"] == "0167507623"])

print(itemdiscount.item.loc[corporate_db["invoicenumber"] == "0172940316"])
#Binning the selected dataset.
#fulldataset["DISCOUNT"] = pd.qcut(fulldataset["DISCOUNT"],10,duplicates="drop")
#merged_left["DISCOUNT"] = pd.qcut(merged_left["DISCOUNT"],10,duplicates="drop")


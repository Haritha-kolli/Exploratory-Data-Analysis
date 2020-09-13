#!/usr/bin/env python
# coding: utf-8

# # Lending Club Case Study

# The objective is to identify the best sectors, countries, and a suitable investment type for making investments. The overall strategy is to invest where others are investing, implying that the 'best' sectors and countries are the ones 'where most investors are investing’.
# 
# 
# Spark Funds has two minor constraints for investments:
#    - It wants to invest between 5 to 15 million USD per round of investment
#    - It wants to invest only in English-speaking countries because of the ease of communication with the companies it would invest in.
# 
# Analysis:
# - Investment type analysis
# - Country Analysis
# - Sector Analysis
# 

# ### Checkpoint 1 -Data Cleaning1

# In[1]:


import pandas as pd
import numpy as np
import plotly.express as px
pd.options.mode.chained_assignment = None
companies = pd.read_csv("companies.csv",engine="python",encoding='palmos')
rounds2 = pd.read_csv("rounds2.csv",engine="python",encoding='palmos')


# In[2]:


companies.info() 


# In[3]:


rounds2.info()


# #### How many unique companies are present in rounds2?
# 
# _observe that 'company_permalink' has duplicates but in diffrent case - It has to be standardised first_

# In[4]:


rounds2.company_permalink


# In[5]:


#Data cleaning applied, standardising the company_permalink case
rounds2.company_permalink = rounds2.company_permalink.apply(lambda x: x.lower())
rounds2.company_permalink.describe()


# #### How many unique companies are present in companies file?

# In[6]:


#standardising the permalink case as well
companies.permalink = companies.permalink.apply(lambda x: x.lower())
companies.permalink.describe()


# #### In the companies data frame, which column can be used as the  unique key for each company? Write the name of the column.
# permalink

# In[7]:


companies.describe()


# #### Are there any companies in the rounds2 file which are not  present in companies ? Answer Y/N.
# No

# #### Merge the two data frames so that all  variables (columns)  in the companies frame are added to the rounds2 data frame. Name the merged frame master_frame. How many observations are present in master_frame ?

# In[8]:


master_frame = rounds2.merge(companies,left_on='company_permalink',right_on='permalink',how='left')


# #### Data Cleaning

# In[9]:


#Analysing the null values in the 'master_frame' dataframe
round(100* master_frame.isnull().sum()/len(master_frame),2)


# In[10]:


master_frame.info()


# In[11]:


#dropping the funding_round_code column ,since it has 73% of null values and it also not that important in our analysis
master_frame.drop(columns=["funding_round_code"],inplace=True)


# In[12]:


#removing the rows where we don't have the 'category_list' and 'country_code' - since all our analysis depends on them.
master_frame.dropna(subset=['category_list','country_code'],inplace=True)


# In[13]:


master_frame["raised_amount_usd"].isnull().sum()


# _filling the na in "raised_amount_usd" with '0'- Assuming that no fund has been raised yet_

# In[14]:


#master_frame.dropna(subset=["raised_amount_usd"],inplace=True)
master_frame["raised_amount_usd"].fillna(value=0,inplace=True)


# _Standardising the raised_amount_usd to Millions._

# In[15]:


master_frame.raised_amount_usd = master_frame.raised_amount_usd.apply(lambda x: round(x/(1000000),2))


# In[16]:


#null values been brought down to 1.5% percentile
(round(master_frame.isnull().sum()/len(master_frame),2)*100).mean()


# ## Check point 2 - Funding Type Analysis
# Filtering out the funding types to ['venture','private_equity','angel','seed'].
# Since, Spark Funds wants to choose one of these four investment types for each potential investment they will make.

# In[17]:


master_frame = master_frame[master_frame.funding_round_type.isin(['venture','private_equity','angel','seed'])]


# In[18]:


master_frame.raised_amount_usd.describe()


# _Removing the outliers is not helping in deciding the funding type - So, I am leaving the funding type outliers as it is_

# In[19]:


#Q1=master_frame.raised_amount_usd.describe()["25%"]
#Q3=master_frame.raised_amount_usd.describe()["75%"]
#IQR=Q3-Q1
#Low=Q1 -(1.5*IQR)
#Up=Q3+(1.5*IQR)
#print(Q1," ",Q3," ",IQR," ",Up ," ",Low)
#master_frame = master_frame[(master_frame.raised_amount_usd <= Up)]


# In[20]:


round(pd.pivot_table(master_frame,index='funding_round_type',values='raised_amount_usd',aggfunc='mean').sort_values(by='raised_amount_usd',ascending=False),2)


# #### Considering that Spark Funds wants to invest between 5 to 15 million USD per  investment round, which investment type is the most suitable for them?
# VENTURE

# In[21]:


#coping the master_frame to 'master' dataframe to use it in plot analysis
master = master_frame
#filtering out the master_frame to 'venture' funding type
master_frame = master_frame[master_frame.funding_round_type == "venture"]


# ### Check Point 3 - Country Analysis
# #### top9  countries, which have received the highest total funding

# In[22]:


#identifying the top 9 countries, which have received the highest total funding
top9Countries = master_frame.groupby(by=["country_code"]).agg({'raised_amount_usd':'sum'}).sort_values(by='raised_amount_usd',ascending=False).head(9).index.values
top9Countries


# #### creating a dataframe named 'top9' with the top9 countries.

# In[23]:


top9 = master_frame.loc[master_frame.country_code.isin(top9Countries)]


# _by checking out the link mentioned, I found out that only 'USA','GBR','IND','CAN' are english spoken countries among the top9_

# In[24]:


EnglishSpokenCountriesInTop9= ('USA','GBR','IND','CAN')


# #### Identify the top three English-speaking countries in the data frame top9.

# In[25]:


#Investment wise
EnglishSpeaking=top9[top9.country_code.isin(EnglishSpokenCountriesInTop9)].groupby(by='country_code').agg({'raised_amount_usd':'sum'}).sort_values(by='raised_amount_usd',ascending=False)
EnglishSpeaking


# In[26]:


px.bar(EnglishSpeaking,color=EnglishSpeaking.index,orientation='h',labels={'index':'country','value':'Amount (Million USD)'})


# ## check point 4 : Sector Analysis
# lets analyse the category_list column

# In[27]:


top9.category_list.value_counts()


# _Extracting primary sector of each category list from the category_list column_

# In[28]:


top9["primary_sector"]=top9["category_list"].apply(lambda x: str(x).split('|')[0])


# importing the 'mapping.csv' file 

# In[29]:


mapping = pd.read_csv("mapping.csv")


# In[30]:


mapping.isnull().sum()


# In[31]:


mapping.dropna(subset=['category_list'],inplace=True)


# In[32]:


mapping.isnull().sum()


# Since we have removed the blank from 'Category_List'- we no need the 'Blanks' column as well. This we can know if we have gone through the data

# In[33]:


mapping.drop(['Blanks'],axis=1)


# we are reshaping the data into friendly form using the melt()

# In[34]:


sector_map=mapping.melt(id_vars="category_list",var_name="main_sector")
sector_map.value.value_counts()


# In[35]:


#filtering out the data and dropping the column 'value' from 'sector_map' dataframe.
sector_map = sector_map.loc[~(sector_map["value"]==0)]
sector_map = sector_map.drop(columns="value")


# _Mapping the "main_sector" values from 'sector_map' dataframe to the "primary_sector" column in top9 dataframe_

# In[36]:


top9["main_sector"] = top9["primary_sector"].map(sector_map.set_index("category_list")["main_sector"])


# ## Checkpoint 5: Sector Analysis 2
#  here in sector analysis, we refer to one of the eight main sectors. 
#  
#  _so we can remove the ones - who doesn't have any main sector out of 8 given main_sectors_

# In[37]:


#null values and shape of top9 before cleaning
print("total null values in main_sector :",top9.main_sector.isna().sum(),"\nshape of top9 : ",top9.shape)


# In[38]:


#dropping the rows who main_secotr is na
top9.dropna(subset=['main_sector'],inplace=True)


# In[39]:


#after dropping the rows
print("total null values in main_sector :",top9.main_sector.isna().sum(),"\nshape of top9 : ",top9.shape)


# _Top 3 English Speaking countries_ - "USA" ,"GBR","IND"
#  And _the most suitable funding type for Spark Funds_ - **VENTURE**

# In[40]:


D1 = top9[top9.country_code=='USA']
D2 = top9[top9.country_code=='GBR']
D3 = top9[top9.country_code=='IND']


# Creating the "Total_No_of_Investments_inEach_MainSector","Total_amount_invested" for the 3 countries dataframes
# 
# 
# _considering the values whose 'raised_amount_usd' >0 , believing that we only need the data where funds amount has been raised_

# In[41]:


country1=D1[D1.raised_amount_usd > 0].set_index("main_sector").groupby(by="main_sector").agg(no_of_Investments=('raised_amount_usd','count'),Amount_Invested=('raised_amount_usd','sum'))
D1["Total_No_of_Investments_inEach_MainSector"] = D1["main_sector"].map(country1["no_of_Investments"])
D1["Total_amount_invested"] =  D1["main_sector"].map(country1["Amount_Invested"])


# In[42]:


country2=D2[D2.raised_amount_usd > 0].set_index("main_sector").groupby(by="main_sector").agg(no_of_Investments=('raised_amount_usd','count'),Amount_Invested=('raised_amount_usd','sum'))
D2["Total_No_of_Investments_inEach_MainSector"] = D2["main_sector"].map(country2["no_of_Investments"])
D2["Total_amount_invested"] =  D2["main_sector"].map(country2["Amount_Invested"])


# In[43]:


country3=D3[D3.raised_amount_usd > 0].set_index("main_sector").groupby(by="main_sector").agg(no_of_Investments=('raised_amount_usd','count'),Amount_Invested=('raised_amount_usd','sum'))
D3["Total_No_of_Investments_inEach_MainSector"] = D1["main_sector"].map(country3["no_of_Investments"])
D3["Total_amount_invested"] =  D1["main_sector"].map(country3["Amount_Invested"])


# Country 1 - USA - analysis

# In[44]:


print("Total number of Investments (count)-",D1.raised_amount_usd.count())
print("Total amount of investment (USD)-",D1.raised_amount_usd.sum())


# In[45]:


country1.sort_values(by="no_of_Investments",ascending=False).head(3)


# _top sector count-wise, which company received the highest investment?_

# In[46]:


D1[(D1.main_sector=="Others")].sort_values(by="raised_amount_usd",ascending=False).name.head(1)


# _second best sector count-wise, which company received the highest investment?_

# In[47]:


D1[(D1.main_sector=="Cleantech / Semiconductors")].sort_values(by="raised_amount_usd",ascending=False).name.head(1)


# Country 2 - GBR - analysis

# In[48]:


print("Total number of Investments (count)-",D2[D2.raised_amount_usd>0].raised_amount_usd.count())
print("Total amount of investment (USD)M-",D2.raised_amount_usd.sum())


# In[49]:


country2.sort_values(by="no_of_Investments",ascending=False).head(3)


# _top sector count-wise, which company received the highest investment?_

# In[50]:


D2[(D2.main_sector=="Others")].sort_values(by="raised_amount_usd",ascending=False).name.head(1)


# _second best sector count-wise, which company received the highest investment?_

# In[51]:


D2[(D2.main_sector=="Cleantech / Semiconductors")].sort_values(by="raised_amount_usd",ascending=False).name.head(1)


# Country 3 - IND - analysis

# In[52]:


print("Total number of Investments (count)-",D3[D3.raised_amount_usd>0].raised_amount_usd.count())
print("Total amount of investment (USD)M-",D3.raised_amount_usd.sum())


# In[53]:


country3.sort_values(by="no_of_Investments",ascending=False).head(3)


# _top sector count-wise, which company received the highest investment?_

# In[54]:


D3[(D3.main_sector=="Others")].sort_values(by="raised_amount_usd",ascending=False).name.head(1)


# _second best sector count-wise, which company received the highest investment?_

# In[55]:


D3[(D3.main_sector=="News, Search and Messaging")].sort_values(by="raised_amount_usd",ascending=False).name.head(1)


# A plot showing the fraction of total investments (globally) in angel, venture, seed, and private equity, and the average amount of investment in each funding type. This chart should make it clear that a certain funding type (FT) is best suited for Spark Funds.

# ## Checkpoint 6 - Plots

# In[62]:


df=master.groupby(by="funding_round_type").agg(total_investments=('raised_amount_usd','count'),average_investment=('raised_amount_usd','mean'))
df['total_investments'] = df['total_investments']/len(master['raised_amount_usd'])
px.scatter(df,x="total_investments",y="average_investment",labels={'total_investments':'Fraction of Total Investments','average_investment':'average amount of investment in Million USD'},color=df.index,size="total_investments").update_layout(
    title="Fraction of total investments(globally) Vs average amount of investment[angel, venture, seed, and private equity]",
    title_font=dict(family="Courier New, monospace",size=13,color="RebeccaPurple"))


# A plot showing the top 9 countries against the total amount of investments of funding type FT. This should make the top 3 countries (Country 1, Country 2, and Country 3) very clear.

# In[57]:


df=top9[(top9['raised_amount_usd']>0)].groupby(by="country_code").agg(total_investments=('raised_amount_usd','sum')).sort_values(by='total_investments',ascending=False)
#& (top9.country_code.isin(EnglishSpokenCountriesInTop9))
px.bar(df,y=df.index,x='total_investments',text='total_investments',color=df.index,title='Top 9 Countries Vs Total Amount of investments of VENTURES Funding Type',
      labels={'total_investments':'Total amount of Investments in Million USD','country_code':'Top 9 Countries'}).update_traces(texttemplate='%{text:.2s}', textposition='outside')


# A plot showing the number of investments in the top 3 sectors of the top 3 countries on one chart (for the chosen investment type FT). 

# _creating three dataframes for 3 countries['main_sector','No_of_investments'] and adding a new derived column 'country'_

# In[58]:


C1=D1[D1.raised_amount_usd>0].groupby(by='main_sector').agg(No_of_investments=('raised_amount_usd','count')).sort_values(by='No_of_investments',ascending=False).head(3)
C1["Country"]="USA"
C2=D2[D2.raised_amount_usd>0].groupby(by='main_sector').agg(No_of_investments=('raised_amount_usd','count')).sort_values(by='No_of_investments',ascending=False).head(3)
C2["Country"]="GBR"
C3=D3[D3.raised_amount_usd>0].groupby(by='main_sector').agg(No_of_investments=('raised_amount_usd','count')).sort_values(by='No_of_investments',ascending=False).head(3)
C3["Country"]="IND"


# _Merging those 3 dataframes , which we created above_

# In[59]:


top3Country_main_sector= pd.concat([C1,C2,C3])


# creating a barplot - showing No:of Investments in the top 3 sectors of the top 3 countries for the **'VENTURES'** Funding Type

# In[60]:


px.bar(top3Country_main_sector,x=top3Country_main_sector.index,y='No_of_investments',labels=
       {'main_sector':'Top 3 main sectors OF top3 Countries'},color='Country',text='No_of_investments',title="No:of Investments in the top 3 sectors of the top 3 countries for the 'VENTURES' Funding Type").update_traces(texttemplate='%{text}', textposition='outside')


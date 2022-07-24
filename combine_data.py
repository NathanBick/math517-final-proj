#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from pathlib import Path
import os
import glob
import math
import pickle

def rstr(df): return df.shape, df.apply(lambda x: [x.unique()])

import networkx as nx
from matplotlib import pyplot as plt
from networkx.algorithms.community import greedy_modularity_communities


# In[4]:


# path may need to be changed
# data_dir = "/Users/NathanBick/Documents/Graduate School/MATH517 - Social Network Analysis/MATH517-final-proj/"
data_dir = "/Users/davidanderson/Desktop/angela/georgetown/social-networks/math517-final-proj/"
#data_dir = "/Users/pamelakatali/Downloads/school/MATH517/math517-final-proj/"

extension = 'csv'
os.chdir(data_dir)
files = glob.glob('*.{}'.format(extension))
print(files)


# Read in the CSV data for the different sub-networks

# In[7]:


linkedin_data = pd.DataFrame()

for file in files:
    print(data_dir + file)
    tmp = pd.read_csv(data_dir + file,skiprows=3)
    tmp['source_file'] = file
    linkedin_data = linkedin_data.append(tmp)


# In[8]:


#print(linkedin_data)
linkedin_data.groupby(['source_file']).count()


# Using the data that we read, create adjacency list for networks using alternate possible definitions of edges:
# 
# * linkedin connection - there would be three main nodes (each of the group members) and then all of those connections in the rows
# * same employer defines an edge - this requires looping through each name to create each as a node. Then loop through the other 

# In[9]:


linkedin_data['Full Name'] = linkedin_data['First Name'] + " " + linkedin_data['Last Name']
nodes = linkedin_data['Full Name'].unique() 
companies = linkedin_data['Company'].unique()
print(nodes)
len(nodes)


# In[10]:


linkedin_data.loc[linkedin_data['Full Name'] == 'David Bick']['Company']


# In[11]:


test =  linkedin_data[linkedin_data['Full Name'] == "David Bick"]["Company"]

test.values[0]


# In[12]:


'''
employer_network = pd.DataFrame()
n = 100
# loop through the unqiue node values. Create a row in the network. 
# For each unique node, loop through all the nodes again, see if the two have the same employer. 
# if they do have the same employer, add to the adjacency list
for node1 in nodes:#[:n]:
    for node2 in nodes:#[:n]:
        if node1 != node2 and isinstance(node1,str) and isinstance(node2,str):
            print("Node1 Name: " + str(node1))
            print("Node2 Name: " + str(node2))
            node1_company = linkedin_data.loc[linkedin_data['Full Name'] == node1]['Company']
            node2_company = linkedin_data.loc[linkedin_data['Full Name'] == node2]['Company']
            print("Node1 Company: " + str(node1_company.values[0]))
            print("Node2  Company: " + str(node2_company.values[0]))
            if node1_company.values[0] == node2_company.values[0]:
                data = [[str(node1),str(node2),str(node1_company.values[0])]]
                # Create the pandas DataFrame
                df = pd.DataFrame(data, columns=['Node1', 'Node2','Company'])
                employer_network = employer_network.append(df)
'''
#pickle.dump(employer_network, open( data_dir + "employer_network.pkl", "wb" ))
employer_network = pickle.load(open( data_dir + "employer_network.pkl", "rb" ) )


# In[15]:


#display(employer_network.tail())


# In[48]:


G=nx.from_pandas_edgelist(employer_network,"Node1","Node2",["Company"])
print("Number of Edges: " + str(nx.number_of_edges(G)))
print("Number of Nodes: " + str(nx.number_of_nodes(G)))


# In[17]:

# first try
plt.figure(3,figsize=(12,12)) 
pos = nx.spring_layout(G,k=10/math.sqrt(G.order()))
nx.draw(G, pos, with_labels=True)
plt.show()

# second try -- try and make the visualization more organized and readable!
values = employer_network.drop('Node2', axis=1).groupby(by=['Node1','Company'], as_index=False).first()
values = values.set_index('Node1')
values = values.reindex(G.nodes())

values['Company'] = pd.Categorical(values['Company'])
values['Company'].cat.codes

df = pd.DataFrame(index=G.nodes(), columns=G.nodes())
for row, data in nx.shortest_path_length(G):
    for col, dist in data.items():
        df.loc[row,col] = dist

df = df.fillna(df.max().max())

plt.figure(3,figsize=(12,12)) 
kamada_pos = nx.kamada_kawai_layout(G, dist=df.to_dict())
nx.draw(G, kamada_pos, cmap=plt.get_cmap('viridis'), node_color=values['Company'].cat.codes, with_labels=True, font_color='black')
# plt.legend(scatterpoints=1)
plt.show()


# In[49]:


# metric 1: degree distribution

degrees = [G.degree(n) for n in G.nodes()]
plt.hist(degrees)
plt.show()


# In[81]:


# metric 2: average path length

# the average path is 1 within each component since the path from one node to
# another (of length 1 edge) is always the shortest path since our network contains
# all possible combinations between every individual that works for the same company
connected_comp_subgraphs = (G.subgraph(c) for c in nx.connected_components(G))
for g in connected_comp_subgraphs: 
    print(g, "has an average path length of", nx.average_shortest_path_length(g))


# In[83]:


# additionally, here's the size of the largest component in terms of n and m
# this metric might be more useful for our analysis, rather than metrics like
# average path length or clustering coefficient. for example, a potential question 
# that this could answer is, "of our connections, where are they most likely to currently work?"
connected_comp_subgraphs = (G.subgraph(c) for c in nx.connected_components(G))
largest_subgraph = max(connected_comp_subgraphs, key = len)
print("The largest component has", largest_subgraph)

# sorted(nx.connected_components(G), key = len, reverse = True)


# In[71]:


# metric 3(a): clustering coefficient of each node

# for unweighted graphs, the clustering of a node is the fraction of possible triangles through that node that exist
# need to noodle on this more to make sure the output of "1" is intuitive here
print(nx.clustering(G))


# In[78]:


# metric 3(b): average clustering of the graph

print("The average clustering coefficient for the graph is", nx.average_clustering(G))


# In[ ]:


# metric 4: C(k) (average degree)

connected_comp_subgraphs = (G.subgraph(c) for c in nx.connected_components(G))
for g in connected_comp_subgraphs: 
    print(g, "has an average degree of", nx.number_of_edges(g))

print("The average degree of all components combined is", round(2 * nx.number_of_edges(G) / nx.number_of_nodes(G), 0))


# In[ ]:
    

# metric 5: number of nodes and edges

print("The total number of nodes and edges is", nx.number_of_nodes(G), "and", nx.number_of_edges(G), ", respectively")


# metric 6: number and size of communities in the graph

c = greedy_modularity_communities(G)
print('Number of ommmunities in the network:', len(c))
print(c)
    
# other questions that could be interesting to answer: what proportion of individuals overlap in their
# company / education / job title connections (i.e. what proportion of those are connected both by company
# and education)?


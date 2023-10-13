import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network


def setcolor(nodetext,att_applicant):
    att_applicant_list = att_applicant.split("|")
    if nodetext in att_applicant_list:
        return "red" 
    elif nodetext.startswith('2') or nodetext.startswith('3') or nodetext.startswith('4') or nodetext.startswith('5'):
        return "lightgreen"
    else:
        return "#ed91ed"

def setsize(nodetext):
    if nodetext.startswith('2') or nodetext.startswith('3') or nodetext.startswith('4') or nodetext.startswith('5'):
        return 20
    else:
        return 10    

def set_title(nodetext,df_merge):
    try:
        deftext = "".join(df_merge[df_merge["fterm"]==nodetext]["説明"].tolist())
        return deftext
    except:
        return "-"


def re_construct_network(edge_df,att_applicant,df_merge):
    #df_merge[["fterm","分野","説明"]]
    #nodeの生成
    G = nx.DiGraph
    G = nx.from_pandas_edgelist(edge_df,source="source",target="target") 

    #node_df生成。一回edgelistからnetworkxを経由してノードリストを生成しておく。
    node_df=pd.DataFrame(list(G.nodes()),columns=['nodes']).sort_values(by='nodes')  
     #この段階でnode_dfに列を追加して属性候補を入れても良い。  

    #edgelistの再生成（）
    edges=[]
    for index, row in edge_df.iterrows():
        edges.append((row[0],row[1]))
    
    #nodeをpyvisに読ませる＋同時にedgeをpyvisに読ませる。
    pyvis_G = Network(height='750px', width='100%')
    node_id = node_df['nodes'].tolist()
    node_x = 1 #lambda式などでの処理もOK
    node_y = 1
    node_value = node_df['nodes'].tolist()
    node_title = node_df['nodes'].apply(set_title,df_merge=df_merge).tolist()
    node_color = node_df['nodes'].apply(setcolor,att_applicant=att_applicant).tolist() #色指定の関数を外に出してlamda式で使う。
    node_label = node_df["nodes"].astype(str).tolist()
    node_size = node_df['nodes'].apply(setsize).tolist() #サイズ指定の関数を外に出してlamda式で使う。
        
    #add_nodesで指定できるのが ["size", "value", "title", "x", "y", "label", "color"]
    pyvis_G.add_nodes(node_id,label=node_label, title=node_title,color=node_color,size=node_size)
    pyvis_G.add_edges(edges)
    pyvis_G.show_buttons(filter_=['physics'])
    #g.toggle_physics(True) #動かしたい場合
    #g.show_buttons(True)   #出力後の調整バーを入れる場合
    #g.show("network_pyvis.html")
    return pyvis_G
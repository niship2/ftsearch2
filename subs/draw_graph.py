#@title グラフ表示用のｄｆ作成
def shorten_applname(name):
    if len(name) <= 30:
        return name
    else:
        return name[0:30] + "..."

graphdf = edgedf2.groupby(["source","target"],as_index=False).size()
graphdf["appcount"] = graphdf["size"]
graphdf["source"] = graphdf["source"].apply(shorten_applname)
graphdf["appl_name"] = graphdf["source"]
graphdf.head()


graphdf.groupby("source").aggregate({"target":"|".join,"appcount":"sum"}).sort_values(by="appcount",ascending=False).head(20)#[["target"]].head(20)


import plotly.express as px
df_dic = {}
tmcs = graphdf["target"].unique().tolist()
for i in tmcs:
    df_dic[i] = graphdf[graphdf["target"] == i][graphdf["source"]!=att_applicant]


topk = 5
appcount_crit= 1
for k,v in df_dic.items():
        ftname = df_dic[k].iloc[0]["target"]
        if(df_dic[k]["appcount"].sum()<appcount_crit):
            pass
        else:
            fig1 = px.bar(df_dic[k].sort_values(by="appcount").head(topk), y='appl_name', x='appcount',
                #title= k + "分野毎出願人上位",
                #facet_col="f_term",
                 text="appcount"
                 )

            fig1.update_layout(font=dict(
            family="Courier New, monospace",
            size=18,  # Set the font size here
            color="RebeccaPurple"
            ))
            fig1.update_layout(yaxis_title=None)
            fig1.update_layout(xaxis_title=None)                #temp_fname = "{}分野データ".format(k)
            fig1.update_layout(
                                    yaxis = dict(
                                    tickfont = dict(size=20)))
            print("-----------------{}--------------------".format(ftname))
            display(fig1)
            print("")
            print("")

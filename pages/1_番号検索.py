import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components


from subs.make_download import make_download_link
from subs.bigQ import get_table_by_appnum

# from subs.bigQ import get_ftermword
from subs.bigQ import agg_applicant
from subs.re_construct_network import re_construct_network

st.set_page_config(layout="wide")

import re


def filter_code(code, options):
    if re.search(code, "|".join(options)):
        return True
    else:
        return False


st.markdown("## 出願番号検索")

url_params = st.experimental_get_query_params()
try:
    appnum_temp = url_params["appnum"][0]
except:
    appnum_temp = "2022076761"
try:
    noiseword_temp = url_params["noiseword"][0]
except:
    noiseword_temp = "####"
try:
    att_applicant = url_params["att_applicant"][0]
except:
    att_applicant = "###"


appnum = st.sidebar.text_input(label="出願番号指定↓", value=appnum_temp, key="0_2_1")
# noiseword = st.sidebar.text_input(label="ノイズワード指定↓",value=noiseword_temp,key="0_2_2")
att_applicant = st.sidebar.text_input(
    label="ハイライト対象出願人(|区切りで複数指定可)↓", value=att_applicant, key="0_2_3"
)
if att_applicant == "":
    att_applicant = "###"


st.markdown("### 関連Fターム（件数少ない分野は省略）")
df, df2 = get_table_by_appnum(appnum)
df = df.rename(columns={"tmc_def": "分野", "def": "説明"})
df2 = df2.rename(columns={"tmc_def": "分野", "def": "説明"})

st.write(df)
# st.write(df2)
df_merge = pd.merge(df, df2).drop(
    columns=["tmc"]
)  # .rename(columns={"tmc_def":"分野","def":"説明"})

# df_merge = df_merge[-df_merge["分野"].str.contains(noiseword)]


with st.sidebar.expander("関連分野一覧", expanded=True):
    st.write(df[["fterm", "分野", "説明"]])

    fname = "分野一覧データ"
    link = make_download_link(df[["fterm", "分野", "説明"]], fname)
    st.write(link, unsafe_allow_html=True)


tmcs = df["fterm"].tolist()

with st.expander("選択したテーマコードに絞り込み", expanded=False):
    option_theme = list(set([x[0:5] for x in tmcs]))
    option_theme.sort()
    options = st.multiselect("", option_theme, option_theme)

df3 = agg_applicant(tmcs, att_applicant)

selected_df3 = df3[df3["f_term"].str.contains("|".join(options))]

with st.expander(
    "分野関連ネットワーク図",
):
    df_draw = selected_df3[
        (selected_df3["appcount"] >= 2)
        | (selected_df3["appl_name"].str.contains(att_applicant))
    ].rename(columns={"appl_name": "source", "f_term": "target", "appcount": "value"})
    df_draw["weight"] = df_draw["value"]
    df_draw["color"] = "blue"

    # st.write(df_draw[df_draw["source"].str.contains("津田")])

    # ネットワークづくり
    pyvis_G = re_construct_network(df_draw, att_applicant, df[["fterm", "分野", "説明"]])
    pyvis_G.write_html("mygraph.html")

    with open("mygraph.html", "rb") as f:
        st.download_button(
            "ネットワーク図ダウンロード", f, file_name="mygraph.html"
        )  # Defaults to 'application/octet-stream'

    with open("mygraph.html", "r") as f2:
        data = f2.read()
        components.html(data, height=750)

    st.write("※線の数字は出願件数")

st.markdown("___")

# st.write(selected_df3)
# st.write(df_merge)

df_dic = {}
for i in tmcs:
    df_dic[i] = pd.merge(
        selected_df3[selected_df3["f_term"] == i][
            -selected_df3["appl_name"].str.contains(att_applicant)
        ],
        df_merge,
        left_on="f_term",
        right_on="fterm",
    )


with st.expander("出願人上位"):
    alldf = pd.merge(
        selected_df3,
        df_merge,
        left_on="f_term",
        right_on="fterm",
    )
    alldf["desc"] = alldf["説明"] + "(" + alldf["fterm"] + ")"
    st.write(
        alldf.groupby("appl_name")
        .agg({"desc": "|".join, "appcount": "sum"})
        .sort_values(by="appcount", ascending=False)
    )


with st.expander("各分野件数"):
    for k, v in df_dic.items():
        try:
            ftname = df_dic[k].iloc[0]["説明"]
            st.write(ftname + "(" + k + ")")
            if df_dic[k]["appcount"].sum() < 3:
                pass
            else:
                fig1 = px.bar(
                    df_dic[k].sort_values(by="appcount"),
                    y="appl_name",
                    x="appcount",
                    # title= k + "分野毎出願人上位",
                    # facet_col="f_term",
                    text="appcount",
                )
                fig1.update_layout(
                    font=dict(
                        family="Courier New, monospace",
                        size=18,  # Set the font size here
                        color="black",
                    )
                )
                fig1.update_layout(yaxis_title=None)
                fig1.update_layout(xaxis_title=None)  # temp_fname = "{}分野データ".format(k)
                fig1.update_layout(yaxis=dict(tickfont=dict(size=20, color="black")))
                st.plotly_chart(fig1)
            # temp_link = make_download_link(df_dic[k].sort_values(by="appcount",ascending=False),temp_fname)
            # st.write(temp_link, unsafe_allow_html=True)
        except:
            pass

st.experimental_set_query_params(
    appnum=appnum,
    # noiseword=noiseword,
    att_applicant=att_applicant,
)

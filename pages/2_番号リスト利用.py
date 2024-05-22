from urllib.error import URLError
import pandas as pd
import networkx as nx
from pyvis.network import Network
import json
import streamlit as st
import streamlit.components.v1 as components
from subs.re_construct_network2 import re_construct_network2
from subs.genai_answer import get_pplx_answer
from mycomponent import mycomponent


if "select_appl_list" not in st.session_state:
    st.session_state.select_appl_list = []

if "att_applicant" not in st.session_state:
    st.session_state.att_applicant = ""

if "select_kw_list" not in st.session_state:
    st.session_state.select_kw_list = []

if "refresh" not in st.session_state:
    st.session_state.refresh = 0


def split_to_list(text, sep):
    return text.split(sep)


def mapping_demo():
    columns = ["出願人", "分析対象項目"]
    init_df = pd.DataFrame(columns=columns)

    with st.expander("データ入力"):
        tab1, tab2 = st.tabs(["コピペ", "ファイルアップロード"])
        with tab1:
            df = st.data_editor(init_df, num_rows="dynamic", use_container_width=False)
            appl_col = "出願人"
            analyze_col = "分析対象項目"

        with tab2:
            uploaded_file = st.file_uploader("分析対象ファイル", type=["xlsx"])

            if uploaded_file:
                df = pd.read_excel(uploaded_file).fillna("-")
                appl_col = "出願人・権利者名"  # st.selectbox("出願人列の指定", df.columns.tolist(), index=8)
                analyze_col = "特徴語"
                # st.selectbox(
                #    "分析対象列の指定", df.columns.tolist(), index=8
                # )

        appl_sep = st.selectbox("出願人列の区切り", ["|", ","])
        analyze_col_sep = st.selectbox("分析対象列の区切り", [",", "|"])

    df[appl_col] = df[appl_col].apply(split_to_list, sep=appl_sep)
    df[analyze_col] = df[analyze_col].apply(split_to_list, sep=analyze_col_sep)

    df_agg = df.explode(appl_col).explode(analyze_col)[[appl_col, analyze_col]]
    # st.write(df_agg)
    df_agg.rename(columns={appl_col: "source", analyze_col: "target"}, inplace=True)

    # @title 特徴語orIPCでedgedfを絞り込む（より関連度高いとこへ）
    with st.expander("描画設定"):
        appl_list = df_agg["source"].value_counts().index.tolist()
        st.session_state.select_appl_list = st.multiselect(
            "描画対象企業の絞り込み", appl_list, default=appl_list[0:10]
        )

        st.session_state.att_applicant = st.selectbox(
            "注目出願人指定（赤丸）",
            st.session_state.select_appl_list,
            index=10,
        )

        att_applicant_kw_list = (
            df_agg[df_agg["source"] == st.session_state.att_applicant]["target"]
            .value_counts()
            .index.tolist()
        )

        word_list = df_agg["target"].value_counts().index.tolist()
        st.session_state.select_kw_list = st.multiselect(
            "キーワード絞り込み", word_list, default=att_applicant_kw_list
        )

        # 指定出願人で絞り込み
        df_agg2 = df_agg[df_agg["source"].isin(st.session_state.select_appl_list)]

        # 指定KWで絞り込み
        df_agg2 = df_agg2[df_agg2["target"].isin(st.session_state.select_kw_list)]
        # edgedf2 = edgedf[edgedf["特徴語"].fillna("-").str.contains(words)]#.groupby("ipc",as_index=False).count().sort_values(by="筆頭出願人・権利者",ascending=False)

    with st.sidebar.expander("出力調整"):
        strength = st.slider("相互反発力", -600, 0, -200)
        spring_constant = st.slider("紐の張力", 0.0, 5.0, 0.01)
        central_gravity = st.slider("重力", 0.0, 1.0, 0.06)
        # max_zoom = st.slider("ボールの大きさ範囲", 1, 100, (25, 75))
        labelsize = st.slider("文字の大きさ", 5, 100, 1)
        edgewidth = st.slider("紐の太さ", 1, 100, 1)

    st.session_state.refresh = st.sidebar.text_input("更新")

    # if st.button("ネットワーク図作成"):

    disp_col1, disp_col2 = st.columns([4, 3])

    with disp_col1:

        file_path = "mycomponent/index.html"
        pyvis_G = re_construct_network2(
            df_agg2,
            headappls=st.session_state.select_appl_list,
            att_applicant=st.session_state.att_applicant,
            strength=strength,
            spring_constant=spring_constant,
            central_gravity=central_gravity,
            max_zoom=10,  # max_zoom,
            labelsize=labelsize,
            edgewidth=edgewidth,
        )
        pyvis_G.write_html(file_path)
        value = mycomponent(
            my_input_value="thre", my_input_value2="the", key=st.session_state.refresh
        )
        # with open(file_path, "r") as f2:
        #    data = f2.read()
        # components.html(data, height=1500)
    with disp_col2:
        try:
            # st.write("Received", json.loads(value))
            jsd = json.loads(value)
            selected_text = st.selectbox("つながり情報選択", jsd)
            query = st.text_area("内容", selected_text)
            if st.button("事業ストーリーを生成"):
                answer = get_pplx_answer(query)
                st.write(answer)
        except:
            pass

    with open(file_path, "rb") as f:
        st.download_button(
            "ネットワーク図DL", f, file_name=file_path
        )  # Defaults to 'application/octet-stream'

    with st.expander("分野毎の出願上位企業"):
        for kw in st.session_state.select_kw_list:
            kw_df = (
                df_agg[df_agg["target"] == kw]["source"]
                .value_counts()[0:10]
                .reset_index()
                .rename(columns={"source": str(kw)})
            )
            if kw_df.shape[0] > 1:
                st.write(kw_df)

    # st.write("※線の数字は出願件数")


st.set_page_config(page_title="Mapping Demo", page_icon="🌍", layout="wide")
mapping_demo()

import requests
import streamlit as st


def get_pplx_answer(query):
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        # "model": "pplx-70b-online",
        "model": "sonar-medium-online",
        "messages": [
            {
                "role": "system",
                "content": (
                    """
           あなたはプロの新規事業開発の担当者です。以下の制約条件と入力文をもとに最高の新規事業創出スト－リーを出力してください。
            # 制約条件:
            ・「A社とB社が**技術でつながっている」という情報から、A社の関連事業内容、B社の関連技術内容をウェブ検索して説明する。
            ・つながりのある技術分野において、どのような新規事業が考えられるか、ストーリーを出力する。
            ・文字数は600文字程度で出力する。
            ・必ず日本語で出力する。
            ・語尾は「です」「ます」を使う。
            ・Be sure to output in Japanese.
            """
                ),
            },
            {"role": "user", "content": query},
        ],
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + st.secrets["PERPLEXITY_API_KEY"],
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()["choices"][0]["message"]["content"]

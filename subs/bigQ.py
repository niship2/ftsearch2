import pandas as pd
import numpy as np
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

client = bigquery.Client(credentials=credentials)

@st.cache_data()
def create_table(n=7):
    df = pd.DataFrame({"x": range(1, 11), "y": n})
    df['x*y'] = df.x * df.y
    return df


def get_table_by_appnum(appnum):
    query = '''
    SELECT SUBSTR(ft.f_term,0,9) as fterm,sub.def,sub2.def as tmc_def
    FROM `techsize.TS_view.ftermtable` as main  ,UNNEST(f_term) as ft
    LEFT JOIN techsize.classtables2.ftermtable as sub
    ON SUBSTR(ft.f_term,0,9) = SUBSTR(sub.fterm,0,9)
    LEFT JOIN techsize.classtables2.ftermtable as sub2
    ON SUBSTR(ft.f_term,0,5) = sub2.fterm
    WHERE app_num = @appnum

    '''
    job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("appnum", "STRING", appnum)
    ]
    )

    
    dataframe = (
    client.query(query, job_config=job_config)
    .result()
    .to_dataframe(
        create_bqstorage_client=True,
        )
    )
    
    
    tmclist = dataframe["fterm"].str[0:5].tolist()
    
    query2 = '''
        SELECT fterm as tmc,def as tmc_def FROM `techsize.classtables2.ftermtable` 
        WHERE REGEXP_CONTAINS(fterm,@tmcs)
        '''
    
    job_config2 = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("tmcs", "STRING", "^" + "$|^".join(tmclist) + "$"),
    ]
    )

    
    dataframe2 = (
    client.query(query2, job_config=job_config2)
    .result()
    .to_dataframe(
        create_bqstorage_client=True,
        )
    )
    
    
    return dataframe,dataframe2



def get_ftermword(wd,noisewd):
    query = '''
        SELECT SUBSTR(fterm,0,5) as tmc,fterm,tree_def,def
        FROM `techsize.classtables2.ftermtable` 
        WHERE REGEXP_CONTAINS(normalize(tree_def,NFKC),normalize(@wd,NFKC))
        AND NOT REGEXP_CONTAINS(normalize(tree_def,NFKC),normalize(@noisewd,NFKC))
        '''

    job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("wd", "STRING", wd),
        bigquery.ScalarQueryParameter("noisewd", "STRING", noisewd),
    ]
    )

    
    dataframe = (
    client.query(query, job_config=job_config)
    .result()
    .to_dataframe(
        create_bqstorage_client=True,
        )
    )
    
    tmclist = dataframe["fterm"].str[0:5].tolist()
    
    query2 = '''
        SELECT fterm as tmc,def as tmc_def FROM `techsize.classtables2.ftermtable` 
        WHERE REGEXP_CONTAINS(fterm,@tmcs)
        '''
    
    job_config2 = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("tmcs", "STRING", "^" + "$|^".join(tmclist) + "$"),
    ]
    )

    
    dataframe2 = (
    client.query(query2, job_config=job_config2)
    .result()
    .to_dataframe(
        create_bqstorage_client=True,
        )
    )
    
    
    return dataframe,dataframe2
    
@st.cache_data()    
def agg_applicant(search_clas):
    query = '''
    WITH ranktable AS(
    SELECT 
    appl_name
    ,ft.f_term
    ,COUNT(*) as appcount
    ,row_number() over(partition by ft.f_term order by COUNT(*) desc) as rank
    FROM `techsize.TS_view.ftermtable` ,UNNEST(f_term) as ft
    WHERE REGEXP_CONTAINS(ft.f_term, @search_clas_list)
    GROUP BY appl_name,ft.f_term
    ORDER BY ft.f_term,appcount DESC
    )
    SELECT appl_name,f_term,appcount 
    FROM ranktable 
    WHERE rank <=6
    AND appl_name is not null
   
        '''
    
    job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("search_clas_list", "STRING", "^" + "$|^".join(search_clas) + "$"),
    ]
    )

    
    dataframe = (
    client.query(query, job_config=job_config)
    .result()
    .to_dataframe(
        create_bqstorage_client=True,
        )
    )
    
    return dataframe
    
import pandas as pd
import base64
import threading
import concurrent.futures
import xlsxwriter
from io import BytesIO
import io

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    #writer.save()
    processed_data = output.getvalue()
    return processed_data


def get_table_download_link(dataframe,fname):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe,fname
    out: href string
    """    
    val = to_excel(dataframe)
    b64 = base64.b64encode(val)  # val looks like b'...'
    #return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="中間データ出力.xlsx">中間データダウンロード</a>'
    return '<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{}" download="{}.xlsx">{}データダウンロード</a>'.format(b64.decode(),fname,fname)



def make_download_link(dataframe,fname):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_table_download_link, dataframe,fname)
        return_value = future.result()
    return return_value 
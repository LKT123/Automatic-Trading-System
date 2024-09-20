import pandas as pd
from io import StringIO

def parse_dataframe(text):
    # 使用StringIO来模拟文件，以便使用pandas的read_csv读取DataFrame
    # 假设DataFrame的列由空格分隔，并忽略索引
    return pd.read_csv(StringIO(text), delim_whitespace=True)

def load_dict_from_text(filepath):
    with open(filepath, 'r') as file:
        content = file.read()

    # 分割字典开始和结束的部分
    dict_content = content.strip("{} \n")
    entries = dict_content.split("', '")
    
    result_dict = {}
    for entry in entries:
        key, df_text = entry.split("':", 1)
        key = key.strip("' ")
        # 解析DataFrame文本，假设DataFrame文本在第一个换行符后开始，且前面有个换行符需要处理
        df = parse_dataframe(df_text.strip().split('\n', 1)[1])
        result_dict[key] = df
    
    return result_dict
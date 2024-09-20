# Data Maintainence
import pandas as pd
import os
import shutil

def data_update(dic):
    # Write the data to the diction
    for key in dic:
        dic[key].to_csv("core/"+key+"_core.csv", index = False)

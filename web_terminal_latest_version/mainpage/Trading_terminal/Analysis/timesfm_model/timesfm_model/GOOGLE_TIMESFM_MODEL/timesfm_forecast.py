from . import timesfm
import pandas as pd
import os
from matplotlib import pyplot as plt
import threading

class timesfm_model:
    
    model_processing_lock = threading.Lock()
    
    def __init__(self, load_model:bool, context_length=64, horizon_length=15) -> None:
        self.have_model = load_model
        if load_model:
            self.tfm = timesfm.TimesFm(
                context_len=context_length,
                horizon_len=horizon_length,
                input_patch_len=32,
                output_patch_len=128,
                num_layers=20,
                model_dims=1280,
                backend="cpu",
            )
            dir_path = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(dir_path, 'timesfm-1.0-200m/checkpoints')
            self.tfm.load_from_checkpoint(repo_id="google/timesfm-1.0-200m", checkpoint_path = file_path)
        else:
            self.tfm = None

    
    def make_a_forecast(self, frequency:str, base:list) -> list:
        """
        @param frequency (str)  : day, month, year
        @param base   (list)    : Input
        """
        if frequency == "day":
            freq = 0
        elif frequency == "month":
            freq = 1
        else:
            freq = 2
        with self.model_processing_lock:
            point_forecast, experimental_quantile_forecast = self.tfm.forecast([base], freq=[freq])
        
        
        return point_forecast[0]






# df_stock = pd.read_csv(r"data/qqq.csv")
# df_inflation = pd.read_csv(r"data/Core Inflation Rate YoY.csv")


# stock_list = df_stock['Close'].tolist()
# inflation_list = df_inflation['Current'].tolist()
# #rint(stock_list)
# #rint(inflation_list)


# condition_list = stock_list[:len(stock_list) - 15]

# drawing_list = stock_list[len(stock_list) - 20:len(stock_list) - 15]
# actual_list = stock_list[len(stock_list) - 20:]


# tfm = timesfm.TimesFm(
#     context_len=512,
#     horizon_len=15,
#     input_patch_len=32,
#     output_patch_len=128,
#     num_layers=20,
#     model_dims=1280,
#     backend="cpu",
# )
# tfm.load_from_checkpoint(repo_id="google/timesfm-1.0-200m", checkpoint_path = "timesfm-1.0-200m/checkpoints")
# point_forecast, experimental_quantile_forecast = tfm.forecast(
#     [condition_list],
#     freq=[0],
# )
# print(point_forecast)
# for i in point_forecast[0]:
#     drawing_list.append(i)

# fig, axs = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})

#     # 2 Rows, 1 Column
#     # gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])  # Adjust height ratios to change relative sizes

#     # Plotting the first array
#     # axs[0].plot(sorted_result_account_by_profit[i].profit_array)
# axs[0].plot(actual_list, label='Actual', color='blue')
# axs[0].plot(drawing_list, label='Forecast', linestyle='--', color='red')


# axs[0].set_title('Profit tracker')
# axs[0].set_xlabel('Time')
# axs[0].set_ylabel('Value')


#     # Automatically adjust subplot params to give specified padding
# plt.tight_layout()

# plt.savefig(f'result.png')
# print("point_forecast: ", point_forecast)
# print("experimental_quantile_forecast: ", experimental_quantile_forecast)


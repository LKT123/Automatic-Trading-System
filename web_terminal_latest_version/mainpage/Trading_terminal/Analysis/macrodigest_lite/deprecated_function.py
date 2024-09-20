import pandas as pd
import datetime
import pytz
from macrodigest_main import *

def nonfarm_cpi_pce(df_dic: dict):
    current_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
    # check if there's new data on nonfarm and inflation:
    dict_today =  find_current_date_data(df_dic, current_time)
    if "Core Inflation Rate YoY" in dict_today.keys(): # Inflation Day
        cpi_mom = dict_today['Core Inflation Rate MoM']
        cpi_yoy = dict_today['Core Inflation Rate YoY']
        mom_consensus_current_diff = convert_to_float(cpi_mom[3]) - convert_to_float(cpi_mom[1])
        yoy_consensus_current_diff = convert_to_float(cpi_yoy[3]) - convert_to_float(cpi_yoy[1])
        if mom_consensus_current_diff < 0 and yoy_consensus_current_diff < 0:
            return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh']
        elif mom_consensus_current_diff > 0 and yoy_consensus_current_diff > 0:
            return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh']
        elif mom_consensus_current_diff > 0 and yoy_consensus_current_diff == 0:
            return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh']
        elif mom_consensus_current_diff == 0 and yoy_consensus_current_diff > 0:
            return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh']
        elif mom_consensus_current_diff < 0 and yoy_consensus_current_diff == 0:
            return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh']
        elif mom_consensus_current_diff == 0 and yoy_consensus_current_diff < 0:
            return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh']
        else:
            full_scale_cpi = dict_today['Inflation Rate YoY']
            full_scale_cpi_consensus_current_diff = convert_to_float(full_scale_cpi[3]) - convert_to_float(full_scale_cpi[1])
            if full_scale_cpi_consensus_current_diff >= 0:
                return ['Long', 'Inflation Rate YoY', full_scale_cpi_consensus_current_diff, 'Fresh']
            else:
                return ['Short', 'Inflation Rate YoY', full_scale_cpi_consensus_current_diff, 'Fresh']
    elif "Non Farm Payrolls" in dict_today.keys():
        nfp_num = dict_today['Non Farm Payrolls']
        nfp_consensus_current_diff =  convert_to_float(nfp_num[3]) - convert_to_float(nfp_num[1])
        if nfp_consensus_current_diff >= 0:
            return ['Long', 'Non Farm Payrolls', nfp_consensus_current_diff, 'Fresh']
        else:
            return ['Short', 'Non Farm Payrolls', nfp_consensus_current_diff, 'Fresh']            
    elif "Core PCE Price Index MoM" in dict_today.keys():
        pce_mom = dict_today['Core PCE Price Index MoM']
        pce_consensus_current_diff = convert_to_float(pce_mom[3]) - convert_to_float(pce_mom[1])
        if pce_consensus_current_diff >= 0:
            return ['Long', 'Core PCE Price Index MoM', pce_consensus_current_diff, 'Fresh']
        else:
            return ['Short', 'Core PCE Price Index MoM', pce_consensus_current_diff, 'Fresh']
    
    else:
        most_fresh_tag = get_the_most_fresh_tag(df_dic, ['Core Inflation Rate MoM', 'Non Farm Payrolls', 'Core PCE Price Index MoM'])
        if most_fresh_tag == 'Core Inflation Rate MoM':
            cpi_mom_old = find_the_data_with_tags(df_dic, 'Core Inflation Rate MoM')
            cpi_yoy_old = find_the_data_with_tags(df_dic, 'Core Inflation Rate YoY')
            mom_consensus_current_diff_old = convert_to_float(cpi_mom_old[3]) - convert_to_float(cpi_mom_old[1])
            yoy_consensus_current_diff_old = convert_to_float(cpi_yoy_old[3]) - convert_to_float(cpi_yoy_old[1])
            if mom_consensus_current_diff_old < 0 and yoy_consensus_current_diff_old < 0:
                return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            elif mom_consensus_current_diff_old > 0 and yoy_consensus_current_diff_old > 0:
                return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            elif mom_consensus_current_diff_old > 0 and yoy_consensus_current_diff_old == 0:
                return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            elif mom_consensus_current_diff_old == 0 and yoy_consensus_current_diff_old > 0:
                return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            elif mom_consensus_current_diff_old < 0 and yoy_consensus_current_diff_old == 0:
                return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            elif mom_consensus_current_diff_old == 0 and yoy_consensus_current_diff_old < 0:
                return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            else:
                full_scale_cpi_old = find_the_data_with_tags(df_dic, 'Inflation Rate YoY')
                full_scale_cpi_consensus_current_diff_old = convert_to_float(full_scale_cpi_old[3]) - convert_to_float(full_scale_cpi_old[1])
                if full_scale_cpi_consensus_current_diff_old >= 0:
                    return ['Long', 'Inflation Rate YoY', full_scale_cpi_consensus_current_diff_old, 'Old', full_scale_cpi_old[5]]
                else:
                    return ['Short', 'Inflation Rate YoY', full_scale_cpi_consensus_current_diff_old, 'Old', full_scale_cpi_old[5]]
            
        elif most_fresh_tag == 'Core PCE Price Index MoM':
            pce_mom_old = find_the_data_with_tags(df_dic, 'Core PCE Price Index MoM')
            pce_consensus_current_diff_old = convert_to_float(pce_mom_old[3]) - convert_to_float(pce_mom_old[1])
            if pce_consensus_current_diff_old >= 0:
                return ['Long', 'Core PCE Price Index MoM', pce_consensus_current_diff_old, 'Old', pce_mom_old[5]]
            else:
                return ['Short', 'Core PCE Price Index MoM', pce_consensus_current_diff_old, 'Old', pce_mom_old[5]]
        else:
            nfp_num_old = find_the_data_with_tags(df_dic, 'Non Farm Payrolls')
            consensus_current_diff_old =  convert_to_float(nfp_num_old[3]) - convert_to_float(nfp_num_old[1])
            if consensus_current_diff_old >= 0:
                return ['Short', 'Non Farm Payrolls', consensus_current_diff_old, 'Old', nfp_num_old[5]]
            else:
                return ['Long', 'Non Farm Payrolls', consensus_current_diff_old, 'Old', nfp_num_old[5]]   
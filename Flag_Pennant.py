import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import mplfinance as mpf 
from RollingWindow import * 
from Trend_line  import * 
from PIP import * 


class Flag : 
    '''
    - Khởi tạo đối tượng Flag
    '''
    def __init__(self, base : tuple) -> None:
        # điểm bắt đầu xu hướng 
        self.base = base

        # điểm bắt đầu xuất hiện patterns
        self.tip = (-1, -1)

        # điểm xác định patterns
        self.confirm  = (-1, -1)

        self.pennant : bool 

        # chiều rộng, cao của pole 
        self.pole_width = -1 
        self.pole_height = -1 

        # chiều rộng, cao của patters
        self.pattern_width = -1 
        self.pattern_height = -1 

        # đường support, resist 
        self.support_slope = -1
        self.support_int = -1 
        self.resist_slope = -1 
        self.resist_int = -1 


class Flag_Recognize : 
    '''
    - Class nhận dạng Flag / Pennant - bull ? bear pattern dựa vào dữ liệu đầu vào 
    - Hai hướng tiếp  cận : 
        - Tìm kiếm các điểm pip 
        - Tìm kiếm bằng cách fit trendline 
    '''

    def find_flag_patterns_pips(data : np.array, w : int) : 
        rw = RollingWindow(data, w,  False)
        
        # tìm local region
        local_max = rw.find_regional_locals_max()
        local_min = rw.find_regional_locals_min()

        # pending
        pending_bull = None
        pending_bear = None 

        # init result
        bull_pennant = []
        bull_flag = []
        bear_pennant = []
        bear_flag = []

        for i in range(len(data)) : 

            if [i, data[i]] in local_max : 
                pending_bear = Flag((i,  data[i]))

            if [i, data[i]] in local_min : 
                pending_bull = Flag((i, data[i]))

            if pending_bear is not None : 
                if Flag_Recognize.check_bear_pips(data) : 
                    if pending_bear.pennant : bear_pennant.append(pending_bear)
                    else : bear_flag.append(pending_bear)
                pending_bear = None

            if pending_bull is not None : 
                if Flag_Recognize.check_bull_pips(data,  ): 
                    if pending_bull.pennant: bull_pennant.append(pending_bull)
                    else : bull_flag.append(pending_bull)

                pending_bull = None

        return (bull_flag, bull_pennant, bear_flag, bear_pennant)
    


    def check_bull_pips(data: np.array, idx: int, w: int, pending: Flag) :
        
        data_slice = data[pending.base[0] : idx + 1]

        # find top 
        max_idx = data_slice.argmax() + pending.base[0]
        pole_width = max_idx - pending.base[0]
        flag_width  = idx - max_idx

        # điều kiện đảm bảo đủ số pip 
        if flag_width < max(5, w * 0.5) : return False

        # điều kiện chiều rộng 
        if flag_width  > pole_width * 0.5 : return False

        pole_height = data[max_idx] - pending.base[1]
        flag_height = data[max_idx] - data[idx]
        # điều kiện chiều cao 
        if pole_height *0.5 < flag_height : return False

        pip = PIP(data[max_idx : idx + 1], 1, 5 )
        pip_x, pip_y = pip.find_PIP_brute_force()

        if pip_y[2] < pip_y[1] or pip_y[2] < pip_y[3] : return False

        # find resist 
        resist_slope  = (pip_y[2] - pip_y[0]) / (pip_x[2] - pip_x[0])
        resist_int = pip_y[0]

        # find support  
        support_slope = (pip_y[3] - pip_y[1]) / (pip_x[3] - pip_x[1])
        support_int = support_slope * (pip_x[0] - pip_x[1]) + pip_y[1]

        # giao điểm có nằm trong 
        if support_slope != resist_slope : 
            intersect = (support_int - resist_int) / (support_slope - resist_slope)
        else : 
            intersect = flag_width * -100

        if intersect <= pip_x[4] and intersect >= 0 : 
            return False
        if intersect < 0 and intersect > -1.0 * flag_width : 
            return False

        resist_end = pip_y[0] + resist_slope * pip_x[4]
        if pip_y[4] < resist_end : return False

        if support_slope > 0 : pending.pennant = True 
        else : pending.pennant = False 
        
        # khởi tạo đối tượng HS 
        pending.tip = (max_idx, data[max_idx])
        pending.confirm = (idx, data[idx])
        pending.flag_width = flag_width
        pending.flag_width = flag_width
        pending.pole_height = pole_height
        pending.pole_width = pole_width

        pending.support_slope = support_slope
        pending.support_int = support_int 
        pending.resist_slope = resist_int
        pending.resist_int = resist_int

        return True
    

    def check_bear_pips(data: np.array, idx: int, w: int, pending: Flag) :
        
        data_slice = data[pending.base[0] : idx + 1]
        min_idx = data_slice.argmin() + pending.base[0]

        flag_width = idx - min_idx 

        if flag_width < max(5, w * 0.5) : return False

        pole_width = min_idx - pending.base[0]
        if flag_width > pole_width* 0.5 : return False 

        pole_height = pending.base[1] - data[min_idx]
        flag_height = data[min_idx : idx + 1].max() - data[min_idx]

        if flag_height > pole_height * 0.5 : return False

        pip = PIP(data[min_idx : idx + 1],1, 5)
        pip_x, pip_y = pip.find_PIP_brute_force()

        if not (pip_y[2] < pip_y[1] and pip_y[2] < pip_y[3]) : return False

        support_slope = (pip_y[2] - pip_y[0]) / (pip_x[2] - pip_x[0])
        support_int = pip_y[0]

        resist_slope = (pip_y[3] - pip_y[1]) / (pip_x[3] - pip_x[1])
        resist_int = resist_slope * (pip_x[0] - pip_x[1]) + pip_y[1]

        if resist_slope  != support_slope : 
            intersect = (support_int - resist_int) / (support_slope - resist_slope)
        else : 
            intersect = -flag_width * 100

        if intersect <= pip_x[4] and intersect >= 0 : return False

        if intersect < 0 and intersect > -1.0 * flag_width : return False

        support_end = pip_y[0] + support_slope * pip_x[4]
        if pip_y[4] <  support_end : return False 

        if resist_slope > 0 : pending.pennant = True
        else : pending.pennant = False


        pending.tip = (min_idx, data[min_idx])
        pending.confirm = (idx, data[idx])

        pending.flag_height = flag_height 
        pending.flag_width = flag_width 
        pending.pole_width = pole_width
        pending.pole_height = pole_height
        pending.support_slope = support_slope
        pending.support_int = support_int 
        pending.resist_int = resist_int 
        pending.resist_slope = resist_slope

        return True

    def find_flag_patterns_trendline(data: np.array, w: int) : 
        pass
    

    def show(data : pd.DataFrame, pat: Flag, padding: int = 2) : 
        if padding < 0 : padding = 0

        start_idx = pat.base[0] - padding 
        end_idx = pat.confirm[0] + 1 + padding
        data_slice = data.iloc[start_idx : end_idx]
        idx = data_slice.index

        fig = plt.gcf()
        ax = fig.gca()

        tip_idx = idx[pat.tip[0] - start_idx]
        conf_idx = idx[pat.confirm[0] - start_idx]

        pole_line = [(idx[pat.base[0] - start_idx], pat.base[1]), (tip_idx, pat.tip[1])]
        resist_line = [(tip_idx, pat.resist_int), (conf_idx, pat.resist_int + pat.resist_slope  * pat.flag_width)]
        support_line = [(tip_idx, pat.support_int), (conf_idx, pat.support_int + pat.support_slope * pat.flag_width)]


        mpf.plot(data_slice, alines = dict(alines = [pole_line, resist_line, support_line], color = ['w', 'r', 'g']), type = 'candle', style = 'charles', ax = ax)
        plt.show()
        pass


if __name__ == '__main__' : 
    data = pd.read_csv()
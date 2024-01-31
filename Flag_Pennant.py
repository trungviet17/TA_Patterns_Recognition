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

    def __init__(self, data: np.array) : 
        pass


    def find_flag_patterns_pips(data : np.array, w : int) : 
        



        pass



    def find_flag_patterns_trendline(data: np.array, w: int) : 
        pass
    
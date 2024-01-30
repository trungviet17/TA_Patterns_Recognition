import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from RollingWindow import * 
from collections import deque
import mplfinance as mpf
'''
- Thuộc tính của lớp : 
    - 5 đỉnh thuộc tính của lớp : head, 2 shoulder, 2 armpit 
    - Tìm kiếm breakpoint ( điểm B )

- Chức năng chính của class 
    - Nhận dạng patterns 2 dạng bottom và up 
    - Tính lợi nhuận khi áp dụng thuật toán trên tập giá trị thực 
    - Biểu diễn trên tập giá trị bg
'''
class HS : 
    def __init__(self) -> None:
        self.l_shoulder = (-1, -1)
        self.head = (-1, -1)
        self.r_shoulder = (-1, -1)
        self.l_armpit = (-1, -1)
        self.r_armpit = (-1, -1)
        self.break_point = (-1, -1)
        # self.price_target = self.compute_price_target()

        # thời gian bắt đầu patterns
        self.start_i = -1 
        # giá trị neck bắt đầu của patterns
        self.neck_start = -1 
        # neck kết thúc patterns 
        self.neck_end = -1 
        # slope của neckline 
        self.neck_slope = -1 
        # chiều cao của p2 với neckline 
        self.head_width = -1

        self.pattern_r2 = -1 

    # phân loại 
    def is_Top(self) : 
        return self.head[1] > self.r_shoulder[1]

    def compute_price_target(self) : 
        ns = self.compute_neckline_slope()
        f = lambda x : ns * (x - self.l_armpit[0]) + self.l_armpit[1]
        return abs(self.head[1] - f(self.head[0]))
    
    def compute_width_shoulder (self) :
        return self.r_shoulder[1] - self.l_shoulder[1]

    def compute_neckline_slope (self) : 
        return (self.r_armpit[1] - self.l_armpit[1]) / (self.r_armpit[0] - self.l_armpit[0])
    

class HSRecognize  : 
    def __init__(self, data : pd.Series , w : int) -> None:
        self.data = np.array(data.values)
        self.w = w 
        self.data_label = np.array(data.index)

    '''
    - Hàm dùng để show ra đồ thị 
    '''
    def show(self, pat : list, data : pd.Series) : 
        plt.style.use('dark_background')
        fig = plt.gcf()
        ax = fig.gca()
        idx = data.index
        data = data.iloc[pat.start_i : pat.break_point[0] + 5]
        l0 = [(idx[pat.start_i], pat.neck_start), (idx[pat.l_shoulder[0]], pat.l_shoulder[1])]
        l1 = [(idx[pat.l_shoulder[0]], pat.l_shoulder[1]), (idx[pat.l_armpit[0]], pat.l_armpit[1])]
        l2 = [(idx[pat.l_armpit[0]], pat.l_armpit[1] ), (idx[pat.head[0]], pat.head[1])]
        l3 = [(idx[pat.head[0]], pat.head[1] ), (idx[pat.r_armpit[0]], pat.r_armpit[1])]
        l4 = [(idx[pat.r_armpit[0]], pat.r_armpit[1] ), (idx[pat.r_shoulder[0]], pat.r_shoulder[1])]
        l5 = [(idx[pat.r_shoulder[0]], pat.r_shoulder[1] ), (idx[pat.break_point[0]], pat.neck_end)]
        neck = [(idx[pat.start_i], pat.neck_start), (idx[pat.break_point[0]], pat.neck_end)]
        mpf.plot(data, alines=dict(alines=[l0, l1, l2, l3, l4, l5, neck ], colors=['w', 'w', 'w', 'w', 'w', 'w', 'r']), type='candle', style='charles', ax=ax)
        
        x = len(data) // 2 - len(data) * 0.1
        if not pat.is_Top():
            y = pat.head[1] + pat.compute_price_target() * 1.25
        else:
            y = pat.head[1] - pat.compute_price_target() * 1.25
        
        ax.text(x,y, f"BTC-USDT 1H ({idx[pat.start_i].strftime('%Y-%m-%d %H:%M')} - {idx[pat.break_point[0]].strftime('%Y-%m-%d %H:%M')})", color='white', fontsize='xx-large')
        plt.show()

    ''' 
    - Hàm dùng để trả về lợi nhuận 
    '''
    def pattern_return (self, data : np.array, pat : HS, percent : bool ) : 
        entry_p = pat.break_point[1]
        entry_i = pat.break_point[0]
        stop_p = pat.r_shoulder
        target_price = 0
        if pat.is_Top() : 
            target_price = pat.neck_end - pat.compute_price_target()
        else : 
            target_price = pat.neck_end + pat.compute_neckline_slope()

        exit_p = -1
        for i in range(pat.head_width) : 
            if entry_p + i >= len(data) : return np.nan

            exit_p = data[entry_i + i]

            if pat.is_Top() and (exit_p < target_price or exit_p > stop_p) : break
            if not pat.is_Top() and (exit_p > target_price or exit_p < stop_p) : break 

        if pat.is_Top() : 
            if percent :  return (entry_p - exit_p) / entry_p 
            else : return entry_p -  exit_p 
        else :
            if percent : return (exit_p - entry_p) / entry_p
            else : return exit_p - entry_p
    
    
    '''
    - Hàm dùng để duyệt và tìm kiếm patterns
    - Trả về đối tượng lớp patterns 
    '''
    def find_hs_pattern(self) : 
        rw = RollingWindow(self.data, self.w, False)
        tops_point = rw.find_regional_locals_max()
        bottoms_point = rw.find_regional_locals_min()

    
        curr_extreme = deque(maxlen = 5)
        type_extreme = deque(maxlen = 5)

        hs_top = []
        hs_bottom = []
        hs_top_alter = True
        hs_bot_alter = True

        
        for i in range(len(self.data)) : 
            
            if [i, self.data[i]] in tops_point : 
                curr_extreme.append(i)
                type_extreme.append(1)
                top_lock = False

            if [i, self.data[i]] in bottoms_point : 
                curr_extreme.append(i)
                type_extreme.append(-1)
                bottom_lock = False
            if len(curr_extreme) < 5 : continue 

            hs_top_alter = True
            hs_bot_alter = True

            if type_extreme[-1] == 1 : 
                for j in range(2, 5) : 
                    if type_extreme[j] == type_extreme[j - 1] : hs_bot_alter = False 
                
                for j in range(1, 4) : 
                    if type_extreme[j] == type_extreme[j - 1] : hs_top_alter = False
                
                bot_extrema = list(curr_extreme)[1:5]
                top_extrema = list(curr_extreme)[0:4]
            else : 
                for j in range(2, 5) : 
                    if type_extreme[j] == type_extreme[j - 1] : hs_top_alter = False 
                
                for j in range(1, 4) : 
                    if type_extreme[j] == type_extreme[j - 1] : hs_bot_alter = False
                top_extrema = list(curr_extreme)[1:5]
                bot_extrema = list(curr_extreme)[0:4]
        
            if bottom_lock or not hs_bot_alter : bot_pat = None 
            else : bot_pat = self.check_bottom_hs(bot_extrema, i)

            if top_lock or not hs_top_alter : top_pat = None 
            else : 
                top_pat = self.check_top_hs(top_extrema, i)
              

            if bot_pat is not None : 
                bottom_lock = True 
                hs_bottom.append(bot_pat)
            
            if top_pat is not None : 
                top_lock = True 
                hs_top.append(top_pat)

        return  hs_top, hs_bottom 

    '''
    - Hàm kiểm tra điều kiện của top patterns 
    '''
    def check_top_hs(self, extreme : list, i : int) : 
        p1 = extreme[0]
        t1 = extreme[1]
        p2 = extreme[2]
        t2 = extreme[3]

        if i - t2 < 2 : return None 

        p3 = t2 + self.data[t2 + 1 : i].argmax() + 1

        if self.data[p2] <= max(self.data[p1], self.data[p3]) : return None 

        r_mid = 0.5 * (self.data[p3] + self.data[t2])
        l_mid = 0.5 * (self.data[p1] + self.data[t1])
        if self.data[p1] < r_mid or self.data[p3] < l_mid : return None 

        if p3 - p2 > 2.5 * (p2 - p1) or p2 - p1 > 2.5 * (p3 - p2) : return None  

        neck_slope = (self.data[t2] - self.data[t1]) / (t2 - t1)

        neck_val = self.data[t1] + (i - t1) * neck_slope 

        if self.data[i] > neck_val : return None 

        head_width = t2 - t1 
        pat_start  =  -1 
        neck_start = -1 

        for j in range(1, head_width ) : 
            neck = self.data[t1] + (p1 - j - t1) * neck_slope

            if p1 - j < 0 : return None 

            if self.data[p1 - j] < neck : 
                pat_start = p1 - j 
                neck_start = neck 

        if pat_start == - 1 : return None 

        res = HS()

        res.l_shoulder = (p1, self.data[p1])
        res.head = (p2, self.data[p2])
        res.r_shoulder = (p3, self.data[p3])
        res.l_armpit = (t1, self.data[t1])
        res.r_armpit = (t2, self.data[t2])
        
        res.start_i = pat_start
        res.neck_start = neck_start
        res.break_point = (i, self.data[i])
        res.neck_slope = neck_slope
        res.neck_end = neck_val 
        res.head_width = head_width 

        return res
    '''
    - Hàm kiểm tra điều kiện của bottom patterns 
    '''
    def check_bottom_hs(self, extreme: list, i : int) : 
        p1 = extreme[0]
        t1 = extreme[1]
        p2 = extreme[2]
        t2 = extreme[3]

        if i - t2 < 2 : return None 

        p3 = t2 + self.data[t2 + 1 : i].argmin() + 1

        if self.data[p2] >= min(self.data[p1], self.data[p3]) : return None 

        r_mid = 0.5 * (self.data[p3] + self.data[t2])
        l_mid = 0.5 * (self.data[p1] + self.data[t1])
        if self.data[p1] > r_mid or self.data[p3] > l_mid : return None 

        if p3 - p2 > 2.5 * (p2 - p1) or p2 - p1 > 2.5 * (p3 - p2) : return None  

        neck_slope = (self.data[t2] - self.data[t1]) / (t2 - t1)

        neck_val = self.data[t1] + (i - t1) * neck_slope 

        if self.data[i] < neck_val : return None 

        head_width = t2 - t1 
        pat_start  =  -1 
        neck_start = -1 

        for j in range(1, head_width ) : 
            neck = self.data[t1] + (p1 - j - t1) * neck_slope

            if p1 - j < 0 : return None 

            if self.data[p1 - j] > neck : 
                pat_start = p1 - j 
                neck_start = neck 

        if pat_start == - 1 : return None 
        
        res = HS()

        res.l_shoulder = (p1, self.data[p1])
        res.head = (p2, self.data[p2])
        res.r_shoulder = (p3, self.data[p3])
        res.l_armpit = (t1, self.data[t1])
        res.r_armpit = (t2, self.data[t2])
        
        res.neck_start = neck_start
        res.break_point = (i, self.data[i])
        res.neck_slope = neck_slope
        res.neck_end = neck_val 
        res.head_width = head_width 

        return res


if __name__ == '__main__' : 
    data = pd.read_csv('Data\BTCUSDT3600.csv')
    
    data['datetime'] = data['datetime'].astype('datetime64[s]')
    data = data.set_index('datetime')


    hs = HSRecognize(data['close'],  6)
    t = hs.find_hs_pattern()
    hs.show(data  = data, pat = t[0][0])
   
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt


'''
- Module tìm kiếm trendline - support và resist trên tập dữ liệu có sẵn 
- 2 Hàm tìm kiếm trendline  trên  1 tập đơn vị dữ liệu, trên tập đơn vị close và open
- Đầu vào : np.array dữ liệu 
- Đầu ra : đường trendline dưới dạng list 
'''

class Trend_line: 

    # Tìm kiếm trendline trên data
    def find_trend_line_single(data: np.array) : 
        # Tìm đường fit với dữ liệu 
        idx = np.arange(len(data))
        [slope, intercept] = np.polyfit(idx, data, 1)
        
        # array đường fit dữ liệu
        line_p = slope * idx + intercept

        # tìm điểm có khoảng cách cao, thấp với đường fit 
        sup_pivot = (data - line_p).argmin()
        resist_pivot =  (data - line_p).argmax()
    
        # xác định đường trendline
        support_line = Trend_line.optimize_slope(True, sup_pivot, slope, data)
        resist_line = Trend_line.optimize_slope(False, resist_pivot, slope, data)

        return (support_line, resist_line)




    def find_trend_line_open_close(high: np.array, low: np.array, close: np.array) : 
        idx = np.arange(len(close))
        (slope, intercept) = np.polyfit(idx, close, 1)

        line_p = slope  *  idx + intercept

        sup_pivot = (low  - line_p).argmin()
        resist_pivot = (high - line_p).argmax()
        

        support_line = Trend_line.optimize_slope(True,sup_pivot, slope, close)
        resist_line = Trend_line.optimize_slope(False, resist_pivot, slope, close)

        return (support_line, resist_line)

    
    # Tìm đường trendline với slope, pivot cho trước
    def optimize_slope(is_sup : bool, pivot: int, init_slope: float, data: np.array) : 
        
        # lượng thay đổi slope - đảm bảo trendline theo đúng chiều của data.max và data.min
        slope_unit = (data.max() - data.min()) / len(data)

        # các giá trị thay đổi
        opt_step = 1.0
        min_step = 0.0001
        curr_step = opt_step

        # Khởi tạo biến kết quả
        best_slope = init_slope
        best_error = Trend_line.check_trend_line(is_sup, pivot, best_slope, data)
      
        assert(best_error >= 0.0)
        # Cờ dùng để thay đổi hướng
        get_derivative = True

        # sai lệch so với best error
        derivative = None

        while  curr_step > min_step : 

            if get_derivative : 
                # tính slope, sai số mới bằng cách tăng 
                new_slope = best_slope + slope_unit * min_step  
                tmp_err = Trend_line.check_trend_line(is_sup, pivot, new_slope, data)
                derivative = tmp_err - best_error
                
                # nếu slope ban đầu ko thỏa mãn, giảm giá trị xuống.
                if tmp_err < 0.0 : 
                    new_slope = best_slope - slope_unit * min_step
                    tmp_err = Trend_line.check_trend_line(is_sup, pivot, new_slope, data)
                    derivative = best_error - tmp_err
                    

                if tmp_err < 0.0 : 
                    raise Exception("Check your data")
                
                get_derivative = False

            # tăng slope -> tăng error -> cần giảm slope 
            if derivative > 0.0 : 
                test_slope = best_slope - slope_unit * curr_step
            else : 
                test_slope = best_slope + slope_unit * curr_step
                
            tmp_err =  Trend_line.check_trend_line(is_sup, pivot, test_slope, data)
            # test_err không thoả mãn hoặc lớn hơn best err => giảm  curr step
            if tmp_err < 0 or tmp_err >= best_error : 
                curr_step *= 0.5
            else : 
                best_error = tmp_err
                best_slope = test_slope
                get_derivative = True

        return (best_slope, -best_slope * pivot + data[pivot])



    # trả về -1 nếu không thỏa mãn, ngược lại trả về khoảng cách giữa các điểm tới data
    def check_trend_line(is_sup: bool, pivot: int, slope: float, data: np.array) : 

        # Tập hợp điểm biểu diễn 
        line_vals = slope*np.arange(len(data)) + (-slope * pivot + data[pivot])

        # khoảng cách giữa đường và dữ liệu
        diff = line_vals - data
       
        # điều kiện đảm bảo trendline
        if is_sup and diff.max() > 1e-5 : return -1.0
        elif not is_sup and diff.min() < -1e-5 : return -1.0 
        
        # bình phương sai số
        err = (diff **2 ).sum()
        return err

    # show trend line tại thời điểm bất kì 
    def show_trend_line(data:np.array, begin:int, end:int, index : np.array) : 
        index = index[begin : end + 1]
        cand = data[begin : end + 1]
        num_idx = np.arange(begin, end + 1)
        support, resist = Trend_line.find_trend_line_single(cand)

        plt.style.use('dark_background')
        plt.plot(num_idx, cand)
        plt.plot(num_idx,  num_idx * support[0] + support[1], color = "red")
        plt.plot(num_idx, num_idx * resist[0] + resist[1], color = "green")
        plt.show()


    def show_all_trendline_slope(data: pd.DataFrame, lookback: int) : 
        data = np.log(data)
        support_slope = [0]* len(data)
        resist_slope = [0] * len(data)

        for i in range(lookback - 1, len(data)) : 
            cand = data.iloc[i -  lookback + 1 : i + 1] 
            support, resist = Trend_line.find_trend_line_single(np.array(cand['close']))

            support_slope[i] = support[0]
            resist_slope[i] = resist[0]
        data['support'] = support_slope
        data['resist'] = resist_slope

        
        fig, ax1 = plt.subplots(figsize = (14, 7))
        
        ax2 = ax1.twinx()
        data['close'].plot(ax=ax1)
        data['support'].plot(ax=ax2, label='Support Slope', color='green')
        data['resist'].plot(ax=ax2, label='Resistance Slope', color='red')
        plt.title("Trend Line Slopes BTC-USDT Daily")
        plt.legend()
        plt.show()



# if __name__ == '__main__' : 
#     data = pd.read_csv('Data\BTCUSDT3600.csv')
#     data['datetime'] = data['datetime'].astype('datetime64[s]')
#     data = data.set_index('datetime')

#     Trend_line.show_all_trendline_slope(data, lookback = 30)
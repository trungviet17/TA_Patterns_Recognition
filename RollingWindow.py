import matplotlib.pyplot as plt


class RollingWindow: 
    def __init__(self, ys, w, pflag):
        self.ys = ys
        self.w = w
        self.pflag = pflag
       
    # draw graph with regional locals
   
    def show_graph(self, res):

        plt.figure(figsize=(20, 10))
        # plt.plot(self.xs, self.ys)
        plt.plot(res.keys(), res.values(), marker='o', linestyle='')
        plt.xlabel("Price")
        plt.ylabel("Time")

        plt.xticks(['2024-01-12 03:30:00', '2023-01-04 01:30:00'])
        plt.show()

    def find_regional_locals_max(self):
        tops = []
        l = len(self.ys)
        for t in range(self.w + 1, l - self.w + 1): 
            if self.ys[t] > max(self.ys[t - self.w: t]) and self.ys[t] > max(self.ys[t+1 : t + self.w + 1]): 
                tops.append([t, self.ys[t]])
        return tops

    def find_regional_locals_min(self):     
        bottoms = []
        l = len(self.ys)
        for t in range(self.w + 1, l - self.w + 1):
            if self.ys[t] < min(self.ys[t - self.w: t]) and self.ys[t] < min(self.ys[t+1 : t + self.w + 1]):        
                bottoms.append([t, self.ys[t]])
        return bottoms

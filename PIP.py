from collections import OrderedDict
import numpy as np 
import matplotlib.pyplot as plt

class My_PIP : 
    def __init__(self, ys, xs, n, method, pflag) :
        self.ys = ys.to_numpy()
        self.xs = np.array([i for i in range(len(xs))])
        self.n = n
        self.method = method
        self.pflag = pflag 
        self.xlabel = xs.tolist()
        self.init_matrix()
        
    # create new matrix Ax, Ay at the first time
    def init_matrix(self) : 
        k = len(self.xs)
        self.matrix_x = [[1 for _ in range(k)]]
        self.matrix_y = [[0 for _ in range(k)]]
        for i in range(1, k-1) : 
            if i - 0 <= k - 1 - i : 
                self.matrix_x[0][i] = 0
            else : 
                self.matrix_x[0][i] = k - 1
            self.matrix_y[0][i] = self.ys[self.matrix_x[0][i]]

        self.matrix_x.append(self.matrix_x[0][::-1])
        self.matrix_y.append(self.matrix_y[0][::-1])
        self.matrix_x[0][0] , self.matrix_x[1][0] = np.nan, np.nan
        self.matrix_y[0][0], self.matrix_y[1][0] = np.nan, np.nan
        self.matrix_x[0][k-1], self.matrix_x[1][k-1] = np.nan, np.nan
        self.matrix_y[0][k-1], self.matrix_y[1][k-1] = np.nan, np.nan
        self.matrix_x = np.array(self.matrix_x)
        self.matrix_y = np.array(self.matrix_y)


    # using to compute distance between 2 matrix 
    def caculate_distance (self) : 
        match (self.method) :
            case 0 : 
                return self.find_argmax(self.ED())
            case 1 :                 
                return self.find_argmax(self.PD())
            case 2 : 
                return self.find_argmax(self.VD())
            

    def find_argmax(self, r) : 
        while np.isnan(np.max(r)) : 
            r[np.argmax(r)] = -np.inf
        return np.argmax(r) 
    
    # change matrix after find pip 
    def present_matrix (self, pipx) : 
        self.matrix_x[0][pipx], self.matrix_x[1][pipx] = np.nan, np.nan
        self.matrix_y[0][pipx], self.matrix_y[1][pipx] = np.nan, np.nan

        for i in range(len(self.matrix_x[0])) : 
            if (np.isnan(self.matrix_x[0][i]) ) : continue
            
            if abs(self.matrix_x[0][i] - i) > abs(pipx - i) : 
                self.matrix_x[1][i] = self.matrix_x[0][i]
                self.matrix_x[0][i] = pipx
            elif abs(self.matrix_x[1][i] - i) > abs(pipx - i) : 
                self.matrix_x[1][i] = pipx
            
            self.matrix_y[0][i] = self.ys[int(self.matrix_x[0][i])]
            self.matrix_y[1][i] = self.ys[int(self.matrix_x[1][i])]

    def find_PIP(self) : 
        curr = 0
        res = {}
        res[self.xlabel[0]] = self.ys[0]
        while(curr < self.n - 2) : 
            pipx = self.caculate_distance()
            res[self.xlabel[pipx]]= self.ys[pipx]
            self.present_matrix(pipx)
            curr += 1
        res[self.xlabel[len(self.xs) - 1]] = self.ys[len(self.xs) - 1]
        res = OrderedDict(res)
        if (self.pflag) : 
            self.show_graph(res)
        else : 
            print(res)


    def show_graph(self, res) : 
        plt.figure(figsize=(20, 10))
        plt.plot(self.xlabel, self.ys)
        plt.plot(res.keys(), res.values(), marker = 'o', linestyle = '-') 
        plt.xlabel("Price")
        plt.ylabel("Time")

        plt.xticks(['2024-01-12 03:30:00', '2023-01-04 01:30:00'])
        plt.show()
        
    def ED(self) : 
        return (((self.matrix_x[0] - self.xs)** 2 + (self.matrix_y[0] - self.ys)**2) ** 0.5 
                + ((self.matrix_x[1] - self.xs) **2 + (self.matrix_y[1] - self.ys)**2 )**0.5)

    def PD(self) :
        S = (self.matrix_y[0] - self.matrix_y[1]) / (self.matrix_x[0] - self.matrix_x[1])
        C = self.matrix_y[0] - S * self.matrix_x[0]
        return abs(S * self.xs - self.ys + C) / (S **2 + 1)**0.5

    def VD(self) : 
        S = (self.matrix_y[0] - self.matrix_y[1]) / (self.matrix_x[0] - self.matrix_x[1])
        C = self.matrix_y[0] - S * self.matrix_x[0]
        return abs(S * self.xs - self.ys + C)

"""
- Implement the PIP method:
    Three methods for computing the distance between two points
    Two-option function to find PIP:
        - Brute force appoarch
        - Matrix appoarch
    Using Matplotlib to visualize the points that we find
"""
class PIP: 
    def __init__(self, data: np.array, method: int, num_pip: int) : 
        self.data = data
        self.method = method
        self.n_pip = num_pip

    # brute force appoarch
    def find_PIP_brute_force(self) :

        pip_x = [0, len(self.data) - 1]
        pip_y = [self.data[0], self.data[-1]]

        for curr in range(2, self.n_pip) : 
            
            max_diff = 0
            max_idx = 0 
            insert_idx = -1 

            for k in range(0, curr - 1) : 
                
                left = k 
                right = k +1
                slope = (pip_y[right]  - pip_y[left]) / (pip_x[right] - pip_x[left])

                c = pip_y[left] - slope * pip_x[left]

                for p in range(pip_x[left] + 1, pip_x[right] ) : 
                    dis = 0
                    if self.method == 1 : 
                        dis = ((p - pip_x[left])**2 + (self.data[p] - pip_y[left]) ** 2) ** 0.5 + (
                            ((p - pip_x[right])) **2 + (self.data[p] - pip_y[right]) **2
                        )
                    elif self.method == 2 : 
                        dis = abs(slope * p - self.data[p] + c) / (slope ** 2 - 1 )**0.5
                    else : 
                        dis = abs(slope * p - self.data[p] + c)

                    if dis > max_diff : 
                        insert_idx = right
                        max_diff = dis 
                        max_idx = p

            pip_x.insert(insert_idx, max_idx)
            pip_y.insert(insert_idx, max_diff)


        return pip_x, pip_y

    # optimize appoarch
    def find_PIP_matrix_optimization(self) : 
        pass


    def show(self) :
        pip_x, pip_y = self.find_PIP_brute_force()
        plt.figure(figsize =  (10, 5))
        plt.plot(data= self.data)
        plt.plot(pip_x, pip_y, color = 'red', label = 'PIP')
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.show()
        



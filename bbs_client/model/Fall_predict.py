import numpy as np


#Shumway-Cook 1997
data_xy = np.array([56.1169984522918, 10.31312237548049,
54.742515218143986, 14.371787321813798,
53.846300444781136, 19.369286722557746,
52.68559625235633, 24.99104815059229,
51.36745788191845, 32.1748703091569,
50.051805314291286, 41.70244940355526,
48.8955755669258, 51.54297331609052,
47.6844924375368, 59.66459417789468,
46.47324358796042, 67.62996457730992,
45.47312225710894, 74.65842406020374,
44.04826008599694, 81.21694844030668,
42.72879595405999, 87.15076689975997,
40.82450528085132, 91.67670358872981,
39.1310106859928, 94.95322843640041,
36.69426105072517, 97.44642946978415,
34.0970942740716, 98.6891829106975,
29.590499498400497, 99.61410870652432,
23.38593568281156, 100])

FALL_X, FALL_Y = data_xy[::2], data_xy[1::2]
#fall_prd = np.interp(np.arange(57), x[::-1], y[::-1])
class Score_updator():
    def __init__(self, fn=None):
        """! Keep track of BBS scores and make fall danger predictions

    @param fn filename to save BBS scores    

    @see [Usefulness of the Berg Balance Scale in Stroke Rehabilitation: A Systematic Review](https://doi.org/10.2522/ptj.20070205)
    
    @remark
    Refer to [Chapter 7](https://www.sciencedirect.com/science/article/pii/B9780323609128000075) of *Guccione's Geriatric Physical Therapy* for in-depth discussion on 
    using BBS score as fall predictor.
"""

        if fn is not None:
            self.fn = fn
            try:
                self.load_txt(fn)
            except:
                print("[Score Updator] Can't load score file", fn)
                print("[Score Updator] Creating a new score file")
                self._score_dict = dict([(act,sc) for act, sc in zip(range(1,15), [-1]*14)])    
        else:
            self._score_dict = dict([(act,sc) for act, sc in zip(range(1,15), [-1]*14)])
        
    def load_txt(self, fn):
        new_scores = []
        with open(fn, "r") as f:
            l = f.readline()
            for l in f.readlines():
                act, sco = l.rstrip().split(":")
                new_scores.append((int(act), int(sco)))
                f.close()
        
        self._score_dict = dict(new_scores)
        
    def update(self, action, score):
        self._score_dict.update({action: score})
        self.write_txt(self.fn)
        
    def text_output(self):
        scores = self._score_dict
        return f"""Action :  Score  
1     :    {scores[1]}   
2     :    {scores[2]}   
3     :    {scores[3]}   
4     :    {scores[4]}   
5     :    {scores[5]}   
6     :    {scores[6]}   
7     :    {scores[7]}   
8     :    {scores[8]}   
9     :    {scores[9]}   
10    :    {scores[10]}   
11    :    {scores[11]}   
12    :    {scores[12]}   
13    :    {scores[13]}   
14    :    {scores[14]}   """

    def write_txt(self, fn=None):
        if fn == None: fn = self.fn
        with open(fn, "w") as f:
            f.write(self.text_output())

    def get_sum(self):
        dsum = []
        for dd, vv in self._score_dict.items():
            if vv < 0:
                print("[Score_Updator] Warning: Not all actions are assessed!!")
                return -1
            dsum.append(vv)

        return sum(dsum)

    def _fall_pred(self, tot):
        return np.interp(tot, FALL_X[::-1], FALL_Y[::-1])

    def get_fall_prediction(self):
        tot = self.get_sum()
        bins = [0,39,52,57]
        if tot < 0:
            return "낙상 예측을 위해 모든 항목을 측정해주세요"
        elif tot < 39:
            return f"총점 {tot}\n" + f"6개월 내 낙상 위험이 {self._fall_pred(tot) :.0f}%로 매우 높습니다!!"
        elif tot < 52:
            return f"총점 {tot}\n" + f"6개월 내 낙상의 위험이 {self._fall_pred(tot) :.0f}% 입니다. 조심하세요."
        elif tot < 57:
            return f"총점 {tot}\n" + "낙상의 위험이 낮습니다."
        else: 
            return -1
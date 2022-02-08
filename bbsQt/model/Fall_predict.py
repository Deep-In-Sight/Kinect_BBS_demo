import numpy as np

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
                print("Can't load score file", fn)
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
                print("[Score_Updator] ERROR: Not all actions are assessed!!")
                return -1
            dsum.append(vv)

        return sum(dsum)

    def get_fall_prediction(self):
        tot = self.get_sum()
        bins = [0,20,40,57]
        prediction = ["낙상 예측을 위해 모든 항목을 측정해주세요",
                      "낙상 위험이 매우 높습니다!!",
                      "낙상의 위험이 있습니다. 조심하세요.", 
                      "낙상의 위험이 낮습니다.",
                      -1]

        return prediction[np.digitize(tot, bins)]
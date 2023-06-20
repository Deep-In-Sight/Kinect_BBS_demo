from encryptor import HEAANEncryptor
import os 
import pickle
import torch
from fase.hnrf.hetree import HNRF
from fase.hnrf import heaan_nrf
from fase.hnrf.tree import NeuralTreeMaker


class HEAANEncryptorDebug(HEAANEncryptor):
    def __init__(self, server_url, cert, work_dir="./", 
                debug=True):
        super().__init__(server_url, cert, work_dir, debug)

    def load_models(self):
        self.models = {}
        dilatation_factor = 10
        polynomial_degree = 10

        self.my_tm_tanh = NeuralTreeMaker(torch.tanh, 
                            use_polynomial=True,
                            dilatation_factor=dilatation_factor, 
                            polynomial_degree=polynomial_degree)
        
    def load_model(self, action, cam):
        
        print("[Evaluator] Loading trained NRF models")

        fn = os.path.join(self.model_dir,f"Nmodel_{action}_{cam}.pickle")
        Nmodel = pickle.load(open(fn, "rb"))
        
        h_rf = HNRF(Nmodel)
        nrf_evaluator = heaan_nrf.HETreeEvaluator.from_model(h_rf,
                                                            self.scheme2,
                                                            self.parms2,
                                                            self.my_tm_tanh.coeffs,
                                                            do_reduction = False,
                                                            #save_check=True
                                                            )
        print("[EVAL.model_loader] HNRF model loaded for class", action)            
        self.models.update({f"{action}_{cam}":nrf_evaluator})    
        
        print("updated models", self.models)    


    def run_model(self, action, cam, ctx):
        self.load_models()
        print("Running a model for class", action)
        try:
            model = self.models[f"{action}_{cam}"]
        except:
            self.load_model(action, cam)
            print(f"Loading a model for class {action} and camera {cam}")
            model = self.models[f"{action}_{cam}"]

        print("[Evaluator] running model...")
        return model(ctx)

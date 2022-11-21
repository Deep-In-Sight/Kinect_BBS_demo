from celery_utils import celery 

@celery.task(bind=True) # bind if access to the instance is needed
def call_heaan(self, fn, action):
    print("HEAAN called")
    
    # do calculation
    # save output file 
    with open(fn, "r") as f:
        new_fn = f.readline()
    
    self.update_state(state="PROGRESS")
        
    with open(new_fn, "w") as f:
        f.write("New file\n")
        f.write("Action", action)

    self.update_state(state="SUCCESS")

    return "HEAAN Inference done!"

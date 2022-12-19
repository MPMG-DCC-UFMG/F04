import gc

def free_object(*args):
    
    for item in args:
        del item
    gc.collect()

    
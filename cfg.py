
cfg = {
    ### Model setting ###
    'model_type': 'classifier', # "classifier" or "regressor"
    'num_HG': 1, # If model_type == "classifier", then use this arg
    'backbone':"mobilenet_v2", # If model_type == "regressor", then use this arg
    ### Scheduler setting ###
    'scheduler_type': 1,  # 0: ReduceLROnPlateau, 1: Warmup_ReduceLROnPlateau 
    'warm_epoch': 2,   # If scheduler == 1, then use warm_epoch arg
    ### training setting ##
    'train_annot':'./data/train_annot.pkl',
    'train_data_root':'./data/train',
    'split_ratio': 0.9,
    'transform':{'flip':False,
                 'roation':True,
                 'noise':True,},
    ### testing data ##
    'test_annot':'./data/val_annot.pkl',
    'test_data_root':'./data/val',
    ### Training hyperparameters ###
    'seed': 987,
    'batch_size': 8,
    'lr': 1e-4,
    'epoch':10,
}
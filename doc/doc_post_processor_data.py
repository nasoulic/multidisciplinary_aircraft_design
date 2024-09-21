import numpy as np

def read_doc_files(config, variant, restype, nsamples):

    '''
    ------------------------------------------------------------------------
    THIS FUNCTION CALCULATES THE MEAN STD & CI OF THE DOC HYBRID-ELECTRIC AIRCRAFT
    VARIANTS MONTE CARLO SIMULATION.

    INPUTS:

    config:  [required] [string]       Configuration name

    variant:  [required] [string]      The variant name

    restype:  [required] [string]      Define the level of detail in doc 
                                        post processing. Acceptable types are:

                                            1. simple   for top-level analysis
                                            2. full    for cost breakdown

    nasmples: [required] [int]         Number of samples

    OUTPUTS:

    csv file.
    ------------------------------------------------------------------------
    '''

    if restype == "simple":
        restype_raw = "simple"
        capital_raw = "Capital"
    elif restype == "full":
        restype_raw = "bkdwn"
        capital_raw = "Aircraft capital"
    else:
        raise ValueError("Wrong input value at restype variable. Acceptable values are 'simple' and 'full'. ")

    with open("./Results/{3}/{0}_doc_results_{1}{2}.csv".format(variant, restype_raw, 0, config), 'r') as f:
        data = f.readlines()
    f.close()

    doc_eval = {}
    total_cost = 0

    for line in data:
        tmp = line.strip("\n").split(",")
        doc_eval[tmp[0]] = [float(tmp[1])]
        total_cost = total_cost + float(tmp[1])
    
    doc_eval["Total annual cost"] = [total_cost]
    doc_eval["Total annual cost wo capital"] = [total_cost - doc_eval[capital_raw][0]]

    for i in range(1, nsamples):

        with open("./Results/{3}/{0}_doc_results_{1}{2}.csv".format(variant, restype_raw, i, config), 'r') as f:
            data = f.readlines()
        f.close()

        total_cost = 0

        for line in data:
            tmp = line.strip("\n").split(",")
            doc_eval[tmp[0]].append(float(tmp[1]))
            total_cost = total_cost + float(tmp[1])

        doc_eval["Total annual cost"].append(total_cost)
        doc_eval["Total annual cost wo capital"].append(total_cost - doc_eval[capital_raw][i])

    eval_dict = {}

    for key, item in doc_eval.items():

        item_ar = np.array(item)

        eval_dict[key] = {}
        eval_dict[key]["mean"] = np.mean(item_ar)
        eval_dict[key]["std"] = np.std(item_ar)
        eval_dict[key]["lower bound"] = eval_dict[key]["mean"] - 1.96 * (eval_dict[key]["std"] / np.sqrt(nsamples))
        eval_dict[key]["upper bound"] = eval_dict[key]["mean"] + 1.96 * (eval_dict[key]["std"] / np.sqrt(nsamples))
        if eval_dict[key]["mean"] > 0:
            eval_dict[key]["plus_minus"] = 1.96 * (eval_dict[key]["std"] / np.sqrt(nsamples))/eval_dict[key]["mean"]*100
        else:
            eval_dict[key]["plus_minus"] = 0

    with open("./Results/{2}/{0}_doc_results_{1}_total.csv".format(variant, restype_raw, config), 'w+') as f:
        for key, item in eval_dict.items():
            f.write("%s\n" %key)

            for inkey, initem in item.items():
                f.write("%s, %f\n" %(inkey, initem))
            
            f.write("\n\n")

    f.close()

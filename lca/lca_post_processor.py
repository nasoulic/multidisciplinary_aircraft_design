import numpy as np
import matplotlib.pyplot as plt

def read_lca_files(variant, EIS, nsamples, el_prod_mtd):

    '''
    ------------------------------------------------------------------------
    THIS FUNCTION CALCULATES THE MEAN STD & CI OF THE LCA HYBRID-ELECTRIC AIRCRAFT
    VARIANTS MONTE CARLO SIMULATION.

    INPUTS:

    variant: [required] [string]       Name of the hybrid variant

    EIS: [required] [int]              Entry Into Service date

    nasmples: [required] [int]         Number of samples

    OUTPUTS:

    csv file.
    ------------------------------------------------------------------------
    '''

    with open("./Results/{0}/lca_inputs_{1}_{2}_output_{3}.csv".format(variant, EIS, 0, el_prod_mtd), 'r') as f:
        data = f.readlines()
    f.close()

    dict_eval = {}
    tot_score = 0
    i = 0

    for line in data:
        if line != "\n":
            tmp = line.strip("\n").split(",")
            dict_eval[tmp[0]] = [float(tmp[1])]
            tot_score += float(tmp[1])
        else:
            i += 1

    dict_eval["single_score"] = [tot_score/(i - 1)]

    for i in range(1, nsamples):

        with open("./Results/{0}/lca_inputs_{1}_{2}_output_{3}.csv".format(variant, EIS, i, el_prod_mtd), 'r') as f:
            data = f.readlines()
        f.close()

        tot_score = 0
        j = 0

        for line in data:
            if line != "\n":
                tmp = line.strip("\n").split(",")
                dict_eval[tmp[0]].append(float(tmp[1]))
                tot_score += float(tmp[1])
            else:
                j += 1

        dict_eval["single_score"].append(tot_score/(j - 1))

    eval_dict = {}

    for key, item in dict_eval.items():

        item_ar = np.array(item)

        eval_dict[key] = {}
        eval_dict[key]["mean"] = np.mean(item_ar)
        eval_dict[key]["std"] = np.std(item_ar)
        eval_dict[key]["lower bound"] = eval_dict[key]["mean"] - 1.96 * (eval_dict[key]["std"] / np.sqrt(nsamples))
        eval_dict[key]["upper bound"] = eval_dict[key]["mean"] + 1.96 * (eval_dict[key]["std"] / np.sqrt(nsamples))
        if eval_dict[key]["mean"] != 0:
            eval_dict[key]["plus_minus"] = 1.96 * (eval_dict[key]["std"] / np.sqrt(nsamples))/eval_dict[key]["mean"]*100
        else:
            eval_dict[key]["plus_minus"] = 0

    with open("./Results/{0}/lca_inputs_{1}_output_{2}_total.csv".format(variant, EIS, el_prod_mtd), 'w+') as f:
        for key, item in eval_dict.items():
            f.write("%s\n" %key)

            for inkey, initem in item.items():
                f.write("%s, %f\n" %(inkey, initem))
            
            f.write("\n\n")

    f.close()

def create_donut_charts(data, el_mtd, weight_type):
    for outer_key, inner_dict in data.items():
        labels = inner_dict.keys()
        values = inner_dict.values()
        total_score = sum(values)

        fig, ax = plt.subplots()
        ax.pie([total_score], radius=0.6, colors=['white'])
        wedges, texts, autotexts = ax.pie(
            values, radius=0.75, autopct='%1.2f%%', startangle=90, pctdistance=0.85,
            labels=[lab.replace("Share of ", "") for lab in labels], textprops={'weight': 'bold'}
        )

        # Add a center circle to make it a donut chart
        center_circle = plt.Circle((0, 0), 0.6, color='white', fc='white')
        fig.gca().add_artist(center_circle)

        # Round the total score to the 4th decimal point
        total_score = round(total_score, 4)

        # Add the "Single Score" label in the center
        ax.text(0, 0, f"Single Score\n{total_score}", ha='center', va='center', fontsize=14, fontweight='bold')

        # Set aspect ratio to equal to make it a circle
        ax.axis('equal')

        # Set chart title in bold
        ax.set_title(outer_key, fontweight='bold', fontsize = 18)

        # Display the chart
        plt.savefig("{0}_{1}_{2}.png".format(outer_key, el_mtd, weight_type), dpi = 300)

        plt.close()
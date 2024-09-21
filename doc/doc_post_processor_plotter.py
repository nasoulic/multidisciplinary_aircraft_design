import numpy as np
import matplotlib.pyplot as plt
import random


def compare_variants(vars, ctype = "simple", capital = True):

    '''
    ------------------------------------------------------------------------
    THIS FUNCTION COMPARES THE DOC EVALUATION OF HYBRID-ELECTRIC AIRCRAFT
    VARIANTS.

    INPUTS:

    vars:  [required] [list]           A list of objects, with each object
                                        being a hybrid variant for
                                        comparison

    ctype: [optional] [string]         Define the level of detail in doc 
                                        post processing. Acceptable types are:

                                            1. simple   for top-level analysis
                                            2. full     for cost breakdown

    capital: [optional] [bool]          Include capital costs in DOC or not.

    OUTPUTS:

    radar plot in .png format with 600 dpi resulution
    ------------------------------------------------------------------------
    '''

    if ctype != "simple" and ctype != "full":
        raise ValueError("Wrong input value at ctype optional variable. Acceptable values are 'simple' and 'full'. ")


    doc_labels = []

    if ctype == "simple":
        for key in vars[0].annual_abs.keys():
            if not capital: 
                if not key == "Capital":
                    doc_labels.append(key)
            else:
                doc_labels.append(key)
    else:
        for key in vars[0].direct_operating_cost_breakdown.keys():
            if not capital:
                if not key == 'Aircraft capital':
                    doc_labels.append(key)
            else:
                doc_labels.append(key)


    doc_labels = [*doc_labels, doc_labels[0]]

    for i in range(len(doc_labels)):
        doc_labels[i] = doc_labels[i] + ' M[\N{euro sign}]'

    doc_label_loc = np.linspace(start = 0, stop = 2*np.pi, num = len(doc_labels))

    res_ar = []
    res_ar_labels = []

    for var in vars:
        res_ar_inner = []

        if ctype == "simple":
            for key, item in var.annual_abs.items():
                if not capital:
                    if not key == "Capital":
                        res_ar_inner.append(item*1e-6)
                else:
                    res_ar_inner.append(item*1e-6)
        else:
            for key, item in var.direct_operating_cost_breakdown.items():
                if not capital:
                    if not key == 'Aircraft capital':
                        res_ar_inner.append(item*1e-6)
                else:
                    res_ar_inner.append(item*1e-6)

        res_ar_inner = [*res_ar_inner, res_ar_inner[0]]
        res_ar.append(res_ar_inner)
        res_ar_labels.append(var.name)

    if ctype == "simple":
        upper_lim = 4
        segs = 8
        if not capital:
            fname = "DOC_comparison_EIS{0}_wo_capital.png".format(vars[-1].EIS)
        else:
            fname = "DOC_comparison_EIS{0}_with_capital.png".format(vars[-1].EIS)
    else:
        upper_lim = 3.5
        segs = 7
        if not capital:
            fname = "DOC_comparison_EIS{0}_breakdown_wo_aircraft_capital.png".format(vars[-1].EIS)
        else:
            fname = "DOC_comparison_EIS{0}_breakdown_with_aircraft_capital.png".format(vars[-1].EIS)


    plt.figure(figsize = (8, 6))
    ax = plt.subplot(polar = True)
    plt.title("Direct Operating Cost comparison EIS {0}".format(vars[-1].EIS))

    ax.set_rlim(0, upper_lim)
    ax.set_rgrids([0.5*(1 + i) for i in range(segs)])

    if len(res_ar) == 3:
        color_list = ['black', 'cyan', 'green']
    else:
        color_list=["#"+''.join([random.choice('0123456789ABCDEF') for i in range(6)])
                for j in range(len(res_ar))]

    for col, res, lab in zip(color_list, res_ar, res_ar_labels):
        plt.plot(doc_label_loc, res, label = lab, color = col)
        plt.fill(doc_label_loc, res, col, alpha = 0.1)

    lines, labels = plt.thetagrids(np.degrees(doc_label_loc), labels = doc_labels)
    for label, ang in zip(ax.get_xticklabels(), doc_label_loc):
        if ang == np.pi*2 or ang == 0:
            label.set_horizontalalignment('left')
        elif ang == np.pi/2 or ang == np.pi/2*3:
            label.set_horizontalalignment('center')
        elif ang == -np.pi:
            label.set_horizontalalignment('right')
        elif ang > 3*np.pi/2 or ang < np.pi/2:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')

    plt.legend(bbox_to_anchor=(1.35, 1.0))
    plt.savefig(fname, dpi = 600)
    plt.close()
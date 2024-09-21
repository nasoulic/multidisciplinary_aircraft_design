def find_in_data(myarray):

    '''
    --------------------------------------------------
    Find pair of points that have the same attribute

    INPUTS:
    myarray :           a nx3 array

    OUTPUTS:
    mylist  :           list of different efficiency values
    ind     :           index of points @ each efficiency

    The first two columns are x and y coordinates respectively
    The third column is the point attribute

    EXAMPLE:

    Let data be an n x 3 array with the 3rd column being
    the efficiency contour of the system

    This function returns the efficiency contour lines
    --------------------------------------------------
    '''

    mylist = []
    for line in myarray:
        if line[2] not in mylist:
            mylist.append(line[2])

    ind = []
    for i in range(len(mylist)):
        ind.append(myarray[:, 2] == mylist[i])

    return mylist, ind
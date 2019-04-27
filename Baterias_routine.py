from Bateria import Bateria
from collections import defaultdict
import numpy as np
from matplotlib import pyplot as plt

load = True

angles = [0,3,6,9,12,15,18]

folderpath = "Domingo (31-03-2019)"

CL_dict = defaultdict(list)
CD_dict = defaultdict(list)
CM_dict = defaultdict(list)

test_number = 1
has_more_tests = True
for incidency in angles:
    has_more_tests = True
    while has_more_tests:
        if load:
            filename = "C{}-{}.txt".format(incidency, test_number)
        else:
            filename = "S{}-{}.txt".format(incidency, test_number)

        filepath = "Logs/{}/{}".format(folderpath, filename)

        bateria = Bateria(
            filepath = filepath,
            skipable_rows = [0,1,2,3,4,5,7],
            bancada_incidency = incidency,
            wing_area_ref = 0.45,
            wing_chord_ref = 0.25,
            toller_acc_horz=1.5,
            toller_acc_vert=5,
            bancada_susp_mass=5,
            ok_min_velocity=9,
        )

        print()

        if bateria.test_exists:
            print('Incidency: {} // Test: {}'.format(incidency, test_number))
            print(bateria.CL_mean)
            print(bateria.CD_mean)
            print(bateria.CM_mean)

            CL_dict[incidency].append(bateria.CL_mean)
            CD_dict[incidency].append(bateria.CD_mean)
            CM_dict[incidency].append(bateria.CM_mean)

            test_number += 1
        else:
            has_more_tests = False
            print('No more tests')
            test_number = 1

        print()
        print('---------------------------------------------------------------')


CL_list = {}
CD_list = {}
CM_list = {}

CL_mean = {}
CD_mean = {}
CM_mean = {}

CL_std = {}
CD_std = {}
CM_std = {}

for inc in angles:

    if CL_dict[inc]:
        CL_list[inc] = CL_dict[inc]
        CD_list[inc] = CD_dict[inc]
        CM_list[inc] = CM_dict[inc]

        CL_mean[inc] = np.mean(CL_dict[inc])
        CD_mean[inc] = np.mean(CD_dict[inc])
        CM_mean[inc] = np.mean(CM_dict[inc])

        CL_std[inc] = np.std(CL_dict[inc])
        CD_std[inc] = np.std(CD_dict[inc])
        CM_std[inc] = np.std(CM_dict[inc])

        print('Incidency angle: {}'.format(inc))

        print('CL list: {} \t CL mean: {} \t CL std deviation: {}'.format(CL_list[inc], CL_mean[inc], CL_std[inc]))
        print('CD list: {} \t CD mean: {} \t CD std deviation: {}'.format(CD_list[inc], CD_mean[inc], CD_std[inc]))
        print('CM list: {} \t CM mean: {} \t CM std deviation: {}'.format(CM_list[inc], CM_mean[inc], CM_std[inc]))

        print()
        print('---------------------------------------------------------------')

fig, (ax1, ax2, ax3) = plt.subplots(1, 3)

plt.suptitle('Coeeficient\'s Mean and Std for all tests')

ax1.set_xlabel('Angle of Attack')
ax1.set_ylabel('CL')
ax2.set_xlabel('Angle of Attack')
ax2.set_ylabel('CD')
ax3.set_xlabel('Angle of Attack')
ax3.set_ylabel('CM')

ax1.errorbar(CL_mean.keys(),CL_mean.values(), CL_std.values())
ax2.errorbar(CD_mean.keys(),CD_mean.values(), CD_std.values())
ax3.errorbar(CM_mean.keys(),CM_mean.values(), CM_std.values())
plt.show()
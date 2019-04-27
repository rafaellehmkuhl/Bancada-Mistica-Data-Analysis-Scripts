from coeffs_routine import get_Coeffs
import pandas as pd
from matplotlib import pyplot as plt
from collections import defaultdict

folderpath = "Domingo (31-03-2019)"

velocities = [30,40,50,60]
incidencies = [0,3,6,9,12]
with_load = True

CL_alpha = defaultdict(list)
CD_alpha = defaultdict(list)
CM_alpha = defaultdict(list)

for velocity in velocities:
    for incidency in incidencies:
        if with_load:
            filename = "2. {} kmh - {} graus - Com Asa.txt".format(velocity, incidency)
            try:
                CL, CD, CM = get_Coeffs(folderpath, filename)
                CL_alpha[incidency].append(CL)
                CD_alpha[incidency].append(CD)
                CM_alpha[incidency].append(CM)
            except:
                pass
        else:
            filename = "1. {} kmh - {} graus - Sem Asa.txt".format(velocity, incidency)
            try:
                CL, CD, CM = get_Coeffs(folderpath, filename)
                CL_alpha[incidency].append(CL)
                CD_alpha[incidency].append(CD)
                CM_alpha[incidency].append(CM)
            except:
                pass

CL_alpha_mean = {}
for incidency in CL_alpha.items():
    CL_alpha_mean[incidency[0]] = sum(incidency[1])/float(len(incidency[1]))

CD_alpha_mean = {}
for incidency in CD_alpha.items():
    CD_alpha_mean[incidency[0]] = sum(incidency[1])/float(len(incidency[1]))

CM_alpha_mean = {}
for incidency in CM_alpha.items():
    CM_alpha_mean[incidency[0]] = sum(incidency[1])/float(len(incidency[1]))

CL_alpha_df = pd.DataFrame.from_dict(CL_alpha_mean, orient='index', columns=['CL']).sort_index()
CD_alpha_df = pd.DataFrame.from_dict(CD_alpha_mean, orient='index', columns=['CD']).sort_index()
CM_alpha_df = pd.DataFrame.from_dict(CM_alpha_mean, orient='index', columns=['CM']).sort_index()

print(CL_alpha_df)
print(CD_alpha_df)
print(CM_alpha_df)

fig1, ax1 = plt.subplots()
plt.plot(CL_alpha_df, label='CL')
plt.legend()
plt.grid()

fig2, ax2 = plt.subplots()
plt.plot(CD_alpha_df, label='CD')
plt.plot(CM_alpha_df, label='CM')
plt.legend()
plt.grid()

plt.show()
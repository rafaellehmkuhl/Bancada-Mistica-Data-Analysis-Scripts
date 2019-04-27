from coeffs_routine import get_Coeffs
import pandas as pd
from matplotlib import pyplot as plt

folderpath = "Domingo (31-03-2019)"

velocities = [50]
incidencies = [0,3,6,9,12]
with_load = True

CL_alpha = {}
CD_alpha = {}
CM_alpha = {}

for velocity in velocities:
    for incidency in incidencies:
        if with_load:
            filename = "2. {} kmh - {} graus - Com Asa.txt".format(velocity, incidency)
            CL, CD, CM = get_Coeffs(folderpath, filename)
            CL_alpha[incidency] = CL
            CD_alpha[incidency] = CD
            CM_alpha[incidency] = CM
        else:
            filename = "1. {} kmh - {} graus - Sem Asa.txt".format(velocity, incidency)
            CL, CD, CM = get_Coeffs(folderpath, filename)
            CL_alpha[incidency] = CL
            CD_alpha[incidency] = CD
            CM_alpha[incidency] = CM

CL_alpha_df = pd.DataFrame.from_dict(CL_alpha, orient='index', columns=['CL'])
CD_alpha_df = pd.DataFrame.from_dict(CD_alpha, orient='index', columns=['CD'])
CM_alpha_df = pd.DataFrame.from_dict(CM_alpha, orient='index', columns=['CM'])

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
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
CL_alpha_Bancada = {}
CD_alpha_Bancada = {}
CM_alpha_Bancada = {}

for velocity in velocities:
    for incidency in incidencies:
        if with_load:
            filename = "2. {} kmh - {} graus - Com Asa.txt".format(velocity, incidency)
            CL, CD, CM = get_Coeffs(folderpath, filename)
            CL_alpha[incidency] = CL
            CD_alpha[incidency] = CD
            CM_alpha[incidency] = CM
        else:
            filename = "2. {} kmh - {} graus - Sem Asa.txt".format(velocity, incidency)
            CL, CD, CM = get_Coeffs(folderpath, filename)
            CL_alpha_Bancada[incidency] = CL
            CD_alpha_Bancada[incidency] = CD
            CM_alpha_Bancada[incidency] = CM

CL_alpha_df = pd.DataFrame.from_dict(CL_alpha, orient='index', columns=['CL'])
CD_alpha_df = pd.DataFrame.from_dict(CD_alpha, orient='index', columns=['CD'])
CM_alpha_df = pd.DataFrame.from_dict(CM_alpha, orient='index', columns=['CM'])

print(CL_alpha_df)
print(CD_alpha_df)
print(CM_alpha_df)

plt.plot(CL_alpha_df)
plt.plot(CD_alpha_df)
plt.plot(CM_alpha_df)

plt.show()
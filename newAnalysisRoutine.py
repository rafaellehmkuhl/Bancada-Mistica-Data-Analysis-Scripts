#%% Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% Read file
folderpath = "Domingo (31-03-2019)"
filename = "2. 50 kmh - 12 graus - Com Asa.txt"
filepath = "Logs/{}/{}".format(folderpath, filename)
df_raw = pd.read_csv(filepath, sep='.', delimiter='\t', na_values=['NaN', 'OutOfRange'], skiprows=(0,1,2,3,4,5,7))


#%% Show the first lines of data
df_raw.head()

#%% Plot all the columns
df_raw.plot(subplots=True, figsize=(12,50))

#%% Create a copy of the original dataframe
df = df_raw

#%% Create zeroed time and set as index
df['Tempo zerado'] = df['Tempo'] - df['Tempo'][0]
df = df.set_index('Tempo zerado')

#%% Plot some data to see what it looks like
df.plot(y='Lift', figsize=(12,5))
df.plot(y='Drag', figsize=(12,5))
df.plot(y='Moment', figsize=(12,5))
df.plot(y='Aceleração em Y', figsize=(12,5))

#%% Puts some of the dataframe's columns onto variables so it's easier to manipulate
lift = df[['Lift']]
drag = df[['Drag']]
moment = df[['Moment']]
velocity = df[['Velocidade Ref. - Pitot 1']]
acc_horz = df[['Aceleração em Y']]
acc_vert = df[['Aceleração em Z']]

#%% Define filtering function
def rolling_filter(data, window):
    data_filtered = data.rolling(window=int(window), center=True).mean().fillna(method='ffill').fillna(method='bfill')
    return data_filtered

#%% Filter the data by rolling means
window = 15

lift_filtered = rolling_filter(lift, window)
drag_filtered = rolling_filter(drag, window)
moment_filtered = rolling_filter(moment, window)
velocity_filtered = rolling_filter(velocity, 89)
acc_horz_filtered = rolling_filter(acc_horz, 49)
acc_vert_filtered = rolling_filter(acc_vert, 49)

#%% Plot the filtered data to see what it looks like now
lift[10:30].plot(figsize=(12,5))
velocity[10:30].plot(figsize=(12,5))
lift_filtered[10:30].plot(figsize=(12,5))
velocity_filtered[10:30].plot(figsize=(12,5))

#%% Store filtered data on a new dataframe
df2 = df

df2['Lift filtered'] = lift_filtered
df2['Drag filtered'] = drag_filtered
df2['Moment filtered'] = moment_filtered
df2['Velocity filtered'] = velocity_filtered
df2['Acc_Y filtered'] = acc_horz_filtered
df2['Acc_Z filtered'] = acc_vert_filtered

#%% Calculate some Bancada's data
bancada_susp_mass = 5
bancada_inerc = acc_horz_filtered*bancada_susp_mass
bancada_inerc = rolling_filter(bancada_inerc, 89)
B_wing = 1.8
c_wing = 0.25
S_wing = B_wing*c_wing
rho = 1.225

#%% Define function for removing bad data
def remove_unwanted(dataframe, column_name):
    dataframe.loc[dataframe['Velocity filtered'] < 7, column_name] = None
    dataframe.loc[dataframe['Acc_Y filtered'] < -0.5, column_name] = None
    dataframe.loc[dataframe['Acc_Y filtered'] > +0.5, column_name] = None
    dataframe.loc[dataframe['Acc_Z filtered'] < +8.0, column_name] = None
    dataframe.loc[dataframe['Acc_Z filtered'] > +9.0, column_name] = None
    return dataframe

#%% Remove bad data
df2 = remove_unwanted(df2, 'Lift filtered')
df2 = remove_unwanted(df2, 'Drag filtered')
df2 = remove_unwanted(df2, 'Moment filtered')

#%% Remove Bancada's Drag
df2['Inercia da Bancada'] = bancada_inerc
df2['Drag filtered offseted'] = df2['Drag filtered'] - df2['Inercia da Bancada']


#%% Print drag with and without offset
df2.plot(y="Inercia da Bancada", figsize=(12,5))
df2.plot(y="Drag filtered", figsize=(12,5))
df2.plot(y="Drag filtered offseted", figsize=(12,5))

#%% Calculate aerodynamic coefficients
df2['CL'] = (2*df2['Lift filtered'])/(rho*S_wing*df2['Velocity filtered']**2)
df2['CD'] = (2*df2['Drag filtered offseted'])/(rho*S_wing*df2['Velocity filtered']**2)
df2['CM'] = (2*df2['Moment filtered'])/(c_wing*rho*S_wing*df2['Velocity filtered']**2)

CL_mean = df2['CL'].mean()
CD_mean = df2['CD'].mean()
CM_mean = df2['CM'].mean()

print('CL: {}'.format(CL_mean))
print('CD: {}'.format(CD_mean))
print('CM: {}'.format(CM_mean))

#%% Plot Coefficients
df2.plot(y="CL", figsize=(12,5))
df2.plot(y="CD", figsize=(12,5))
df2.plot(y="Velocity filtered", figsize=(12,5))
df2.plot(y="Acc_Y filtered", figsize=(12,5))
df2.plot(y="Acc_Z filtered", figsize=(12,5))

df2.plot(x="CD", y="CL", figsize=(12,5), kind='scatter')

#%%

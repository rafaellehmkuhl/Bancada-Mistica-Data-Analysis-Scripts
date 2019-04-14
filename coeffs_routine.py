# Import libraries
import pandas as pd
import numpy as np

def get_Coeffs(folderpath, filename):

    # Read file
    filepath = "Logs/{}/{}".format(folderpath, filename)
    df_raw = pd.read_csv(filepath, sep='.', delimiter='\t', na_values=['NaN', 'OutOfRange'], skiprows=(0,1,2,3,4,5,7))

    # Create a copy of the original dataframe
    df = df_raw

    # Create zeroed time and set as index
    df['Tempo zerado'] = df['Tempo'] - df['Tempo'][0]
    df = df.set_index('Tempo zerado')

    # Puts some of the dataframe's columns onto variables so it's easier to manipulate
    lift = df[['Lift']]
    drag = df[['Drag']]
    moment = df[['Moment']]
    velocity = df[['Velocidade Ref. - Pitot 1']]
    acc_horz = df[['Aceleração em Y']]
    acc_vert = df[['Aceleração em Z']]

    # Define filtering function
    def rolling_filter(data, window):
        data_filtered = data.rolling(window=int(window), center=True).mean().fillna(method='ffill').fillna(method='bfill')
        return data_filtered

    # Filter the data by rolling means
    window = 15

    lift_filtered = rolling_filter(lift, window)
    drag_filtered = rolling_filter(drag, window)
    moment_filtered = rolling_filter(moment, window)
    velocity_filtered = rolling_filter(velocity, 89)
    acc_horz_filtered = rolling_filter(acc_horz, 49)
    acc_vert_filtered = rolling_filter(acc_vert, 49)

    # Store filtered data on a new dataframe
    df2 = df

    df2['Lift filtered'] = lift_filtered
    df2['Drag filtered'] = drag_filtered
    df2['Moment filtered'] = moment_filtered
    df2['Velocity filtered'] = velocity_filtered
    df2['Acc_Y filtered'] = acc_horz_filtered
    df2['Acc_Z filtered'] = acc_vert_filtered

    # Calculate some Bancada's data
    bancada_susp_mass = 5
    bancada_inerc = acc_horz_filtered*bancada_susp_mass
    bancada_inerc = rolling_filter(bancada_inerc, 89)
    B_wing = 1.8
    c_wing = 0.25
    S_wing = B_wing*c_wing
    rho = 1.225

    # Define function for removing bad data
    def remove_unwanted(dataframe, column_name):
        dataframe.loc[dataframe['Velocity filtered'] < 7, column_name] = None
        dataframe.loc[dataframe['Acc_Y filtered'] < -0.5, column_name] = None
        dataframe.loc[dataframe['Acc_Y filtered'] > +0.5, column_name] = None
        dataframe.loc[dataframe['Acc_Z filtered'] < +8.0, column_name] = None
        dataframe.loc[dataframe['Acc_Z filtered'] > +9.0, column_name] = None
        return dataframe

    # Remove bad data
    df2 = remove_unwanted(df2, 'Lift filtered')
    df2 = remove_unwanted(df2, 'Drag filtered')
    df2 = remove_unwanted(df2, 'Moment filtered')

    # Remove Bancada's Drag
    df2['Inercia da Bancada'] = bancada_inerc
    df2['Drag filtered offseted'] = df2['Drag filtered'] - df2['Inercia da Bancada']

    # Calculate aerodynamic coefficients
    df2['CL'] = (2*df2['Lift filtered'])/(rho*S_wing*df2['Velocity filtered']**2)
    df2['CD'] = (2*df2['Drag filtered offseted'])/(rho*S_wing*df2['Velocity filtered']**2)
    df2['CM'] = (2*df2['Moment filtered'])/(c_wing*rho*S_wing*df2['Velocity filtered']**2)

    CL_mean = df2['CL'].mean()
    CD_mean = df2['CD'].mean()
    CM_mean = df2['CM'].mean()

    return CL_mean, CD_mean, CM_mean
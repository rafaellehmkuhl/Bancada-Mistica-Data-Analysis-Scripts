import pandas as pd
from matplotlib import pyplot as plt

plt.style.use('seaborn')

class Bateria:
    """Class for storing and returning useful data
    about each one of the test batteries."""

    def __init__(self,
                 filepath,
                 skipable_rows,
                 bancada_incidency,
                 wing_area_ref,
                 wing_chord_ref,
                 bancada_susp_mass = 5,
                 air_density = 1.225,
                 ok_min_velocity = 7.0,
                 toller_acc_horz = 0.5,
                 toller_acc_vert = 0.5,
                 zero_vel = False
                ):

        self.filepath = filepath
        self.skipable_rows = skipable_rows
        self.bancada_incidency = bancada_incidency
        self.bancada_susp_mass = bancada_susp_mass
        self.air_density = air_density
        self.wing_area_ref = wing_area_ref
        self.wing_chord_ref = wing_chord_ref
        self.ok_min_velocity = ok_min_velocity
        self.toller_acc_horz = toller_acc_horz
        self.toller_acc_vert = toller_acc_vert
        self.zero_vel = zero_vel

        self.orig_df = None
        self.fltrd_df = None

        self.test_exists = True

        self.CL_mean = 0
        self.CD_mean = 0
        self.CM_mean = 0

        try:
            self.read_file()
            self.zero_time()

            if self.zero_vel:
                self.zero_velocity()

            self.calculate_min_max_accs()

            self.rename_column('Velocidade Ref. - Pitot 1', 'Velocity')
            self.rename_column('Aceleração em Y', 'Horizontal Acc')
            self.rename_column('Aceleração em Z', 'Vertical Acc')

            self.filter_mean('Lift',            1)
            self.filter_mean('Drag',            1)
            self.filter_mean('Moment',          1)
            self.filter_mean('Velocity',        1)
            self.filter_mean('Horizontal Acc',  1)
            self.filter_mean('Vertical Acc',    1)

            self.remove_unwanted('Lift')
            self.remove_unwanted('Drag')
            self.remove_unwanted('Moment')

            self.calculate_theor_loads()
            self.remove_bancadas_drag()
            self.calculate_coeffs()

            # self.show_loads()

        except FileNotFoundError as e:
            self.test_exists = False

    def zero_velocity(self):
        # print(self.fltrd_df.columns.values)
        densAr = 1.218
        # conv = (self.fltrd_df['Raw Pitot - Pitot 1'] / self.fltrd_df['Velocity']).mean()
        zero_raw = self.fltrd_df['Raw Pitot - Pitot 1'].iloc[1:100].mean()
        self.fltrd_df['Pressao Dinamica Ref.- Pitot 1'] = self.fltrd_df['Pressao Dinamica Ref.- Pitot 1']-zero_raw
        self.fltrd_df['Velocidade Ref. - Pitot 1'] = (self.fltrd_df['Pressao Dinamica Ref.- Pitot 1'].abs()*2/densAr)**0.5

    def calculate_min_max_accs(self):
        self.zero_acc_horz = 0.31
        self.zero_acc_vert = 8.95
        self.ok_min_acc_horz = self.zero_acc_horz - self.toller_acc_horz
        self.ok_max_acc_horz = self.zero_acc_horz + self.toller_acc_horz
        self.ok_min_acc_vert = self.zero_acc_vert - self.toller_acc_vert
        self.ok_max_acc_vert = self.zero_acc_vert + self.toller_acc_vert

    def show_loads(self):
        fig1, ax1 = plt.subplots(figsize=(16,8))
        ax2 = ax1.twinx()
        # self.fltrd_df.plot(y='Lift',                         ax=ax1)
        self.orig_df.plot(y='Lift',                         ax=ax1)
        # self.fltrd_df.plot(y='Drag',                         ax=ax1)
        self.orig_df.plot(y='Drag',                         ax=ax1)
        # self.fltrd_df.plot(y='Drag from load',               ax=ax1)
        # self.fltrd_df.plot(y='Inertia of Bancada',           ax=ax1)
        # self.fltrd_df.plot(y='Moment',                       ax=ax1)
        # self.orig_df.plot(y='Velocidade Ref. - Pitot 1',     ax=ax1)
        self.fltrd_df.plot(y='Velocity',                     ax=ax1)
        # self.fltrd_df.plot(y='Raw Pitot - Pitot 1',          ax=ax2)
        # self.fltrd_df.plot(y='Horizontal Acc',               ax=ax2)
        # self.fltrd_df.plot(y='Vertical Acc',                 ax=ax2)
        # self.fltrd_df.plot(y='CL',                           ax=ax1)
        # self.fltrd_df.plot(y='CD',                           ax=ax1)
        # self.fltrd_df.plot(y='CM',                           ax=ax1)
        # self.fltrd_df.plot(y='Lift Theoretical',             ax=ax1)
        # self.fltrd_df.plot(y='Drag Theoretical',             ax=ax1)
        # self.fltrd_df.plot(y='Drag Difference',              ax=ax1)
        # self.fltrd_df.plot(y='Moment Theoretical',           ax=ax1)
        # self.fltrd_df.plot(y='Horizontal Acc Theoretical',   ax=ax2)

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc=0)
        fig1.tight_layout()
        plt.show()

    def read_file(self):
        self.orig_df = pd.read_csv(self.filepath, sep='.', delimiter='\t', na_values=['NaN', 'OutOfRange'], skiprows=self.skipable_rows)
        self.fltrd_df = self.orig_df.copy()

    def rename_column(self, orig_name, new_name):
        self.fltrd_df.rename(index=str, columns={orig_name: new_name}, inplace=True)

    def zero_time(self):
        self.fltrd_df['Tempo'] = self.fltrd_df['Tempo'] - self.fltrd_df['Tempo'][0]
        self.fltrd_df.set_index('Tempo', inplace=True)

    def filter_mean(self, column_name, window):
        self.fltrd_df[[column_name]] = self.fltrd_df[[column_name]].rolling(window=int(window), center=True).mean().fillna(method='ffill').fillna(method='bfill')

    def remove_unwanted(self, column_name):
        self.fltrd_df.loc[  self.fltrd_df['Velocity']         < self.ok_min_velocity, column_name] = None
        self.fltrd_df.loc[  self.fltrd_df['Horizontal Acc']   < self.ok_min_acc_horz, column_name] = None
        self.fltrd_df.loc[  self.fltrd_df['Horizontal Acc']   > self.ok_max_acc_horz, column_name] = None
        self.fltrd_df.loc[  self.fltrd_df['Vertical Acc']     < self.ok_min_acc_vert, column_name] = None
        self.fltrd_df.loc[  self.fltrd_df['Vertical Acc']     > self.ok_max_acc_vert, column_name] = None

    def calculate_theor_loads(self):
        self.CL_theor = 1.1
        self.CD_theor = 0.3
        self.CM_theor = 0.3
        self.fltrd_df['Lift Theoretical']   = (0.5*self.air_density*self.wing_area_ref*self.CL_theor*self.fltrd_df['Velocity']**2)
        self.fltrd_df['Drag Theoretical']   = (0.5*self.air_density*self.wing_area_ref*self.CD_theor*self.fltrd_df['Velocity']**2)
        self.fltrd_df['Moment Theoretical'] = (0.5*self.wing_chord_ref*self.air_density*self.wing_area_ref*self.CM_theor*self.fltrd_df['Velocity']**2)
        # recv.diff() / recv.index.to_series().diff().dt.total_seconds()
        self.deltaTime = (self.fltrd_df.index.to_series().astype('float64').diff().median())
        self.fltrd_df['Horizontal Acc Theoretical'] = (self.fltrd_df['Velocity'].diff()/self.deltaTime)
        self.filter_mean('Horizontal Acc Theoretical', 149)

    def remove_bancadas_drag(self):
        self.fltrd_df['Inertia of Bancada'] = (self.fltrd_df['Horizontal Acc Theoretical']-self.zero_acc_horz) * self.bancada_susp_mass
        self.fltrd_df['Drag from load'] = self.fltrd_df['Drag'] - self.fltrd_df['Inertia of Bancada']
        self.fltrd_df['Drag Difference'] = self.fltrd_df['Drag'] - self.fltrd_df['Drag Theoretical']

    def calculate_coeffs(self):
        self.fltrd_df['CL'] = (2*self.fltrd_df['Lift'])/(self.air_density*self.wing_area_ref*self.fltrd_df['Velocity']**2)
        self.fltrd_df['CD'] = (2*self.fltrd_df['Drag from load'])/(self.air_density*self.wing_area_ref*self.fltrd_df['Velocity']**2)
        self.fltrd_df['CM'] = (2*self.fltrd_df['Moment'])/(self.wing_chord_ref*self.air_density*self.wing_area_ref*self.fltrd_df['Velocity']**2)

        self.CL_mean = self.fltrd_df['CL'].mean()
        self.CD_mean = self.fltrd_df['CD'].mean()
        self.CM_mean = self.fltrd_df['CM'].mean()
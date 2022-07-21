# %% [markdown]
# # Imports and Reading Data

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('max_columns', 200)

import math
import datetime

# %% [markdown]
# # Raw Solar Data of Cities from PVGIS
# ## Cities include: Brussels, Paris, London, Madrid

# %%
brussels_df = pd.read_csv(r'C:\Users\Redd\Documents\Python Training\Portfolio\2. Solar heating\Brussels Monthly Data.csv', 
                delimiter=',',
                lineterminator='\r',
                skiprows=(0,1,2,3,4))

# %%
brussels_df.columns

# %%
brussels_df = brussels_df[['\nyear',
#                          'Unnamed: 1', 
                          'month',
#                          'Unnamed: 3', 
                          'H(h)_m',
#                          'Unnamed: 5',
                          'H(i_opt)_m',
#                          'Unnamed: 7', 
                          'Hb(n)_m',
#                          'Unnamed: 9', 
                          'Kd',
#                          'Unnamed: 11',
                          'T2m']].copy()
brussels_df.head()

# %%
brussels_df = brussels_df.rename(columns = {'\nyear' : 'year',
                                            'month' : 'month',
                                            'H(h)_m' : 'global_horizontal_irradiation',
                                            'H(i_opt)_m' : 'global_irradiation_optimum_angle',
                                            'Hb(n)_m' : 'direct_normal_irradiation',
                                            'Kd' : 'diffuse_global_ratio',
                                            'T2m' : 'outdoor_temperature'
                                           }
                                )
brussels_df.head()

# %%
brussels_df['year'] = brussels_df['year'].str.replace('\n', '', regex=False)
brussels_df = brussels_df[:36]
brussels_df

# %%
brussels_df.info()

# %%
def month_converter(month):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months.index(month) + 1

# %%
brussels_df['month'] = brussels_df['month'].apply(month_converter)

# %%
brussels_df['year'] = pd.to_numeric(brussels_df['year'])

# %%
brussels_df.info()

# %%
brussels_df['date'] = pd.to_datetime(brussels_df[['year', 'month']].assign(day=1)).dt.date
brussels_df.head()


# %%
diff = brussels_df['date'].diff(periods=-1).dt.days.abs()
diff[35] = 31               #initially NaN for the last month value, place 31 for december

brussels_df['calendar_days'] = diff
brussels_df.tail()


# %%
datelist = [date for date in brussels_df['date']]       #use list to avoid chain indexing
bus_days = [np.busday_count(datelist[i],
                            datelist[i+1]
                            ) for i in range(len(datelist)-1
                                            )
            ]

bus_days.append(bus_days[(35-12)])      #this code is for the last month december 2020 , copying the number of business days of december 2019

brussels_df['business_days'] = bus_days
brussels_df.tail()

# %%
sns.set_theme(style="darkgrid")

plt.rcParams["figure.figsize"] = [15, 3.50]

fig, ax = plt.subplots()
ax1 = sns.lineplot(x='date', y='global_horizontal_irradiation', data=brussels_df, label='Global horizontal irradiation')
ax2 = sns.lineplot(x='date', y='global_irradiation_optimum_angle', data=brussels_df, label='Global irradiation at Optimum angle')
ax3 = sns.lineplot(x='date', y='direct_normal_irradiation', data=brussels_df, label='Direct normal irradiation')
ax.set(xlabel='Months', ylabel='Irradiation (kWh/m2)')
plt.legend(loc='lower left')

# %% [markdown]
# # Generating Water Consumption. Unit: litres of DHWD/day at 60ºC
# ## Reference: Spanish Technical Building Code (CTE)
# 
# ### The litres of DHWD/day at 60ºC in the table have been calculated from Table 1 (average daily unit consumption) of UNE 94002:2005 “Thermal solar systems for domestic hot water production: Calculation method for heat demand.” Equation (3.2) was used for the calculation, with Ti = 12ºC (constant) and T = 45ºC.

# %%
water_consumption_per_person = {'single_family_dwellings' : 30,
                                'multi_family_dwellings' : 22,
                                'hospitals_and_clinics' : 55,
                                '4_star_hotel' : 70,
                                '3_star_hotel' : 55,
                                '2_star_hotel' : 40,
                                'hostel' : 40,
                                'camping' : 40,
                                'boarding_house' : 35,
                                'homes_for_the_elderly' : 55,
                                'student_dormitories' : 55,
                                'dressing_rooms' : 15,
                                'schools' : 3,
                                'barracks' : 20,
                                'factories_and_shops' : 15,
                                'administrative_premises' : 3,
                                'gyms' : 22.5,
                                'restaurants' : 7.5,
                                'cafeterias' : 1
                               }

# %%
data = [('library', 'schools', 1, 30),
        ('office', 'administrative_premises', 4, 4)]
b1_df = pd.DataFrame(data,
                     columns=['room_name', 'room_type', 'room_count', 'people_count'],
                    )
# b1_df.set_index('room_name',
#                 inplace = True
#                )
b1_df

# %%
b1_dict = b1_df.to_dict(orient='records')
b1_dict

# %%
class Room:
    def __init__(self, room_name, room_type, room_count, people_count):
        self.room_name = room_name
        self.room_type = room_type
        self.room_count = room_count
        self.people_count = people_count

# %%
def getWater(room_type, room_count, people_count):
    if room_type in water_consumption_per_person.keys():
        water_consumption = water_consumption_per_person[room_type] * room_count * people_count            
    else:
        print('Please choose from building types from CTE')
        water_consumption = 0
    return water_consumption

# %%
room_list = [Room(**x) for x in b1_dict]
b1_water = 0
for room in room_list:
    b1_water += getWater(room.room_type, room.room_count, room.people_count)
b1_water

# %%
data = [('library', 'schools', 1, 38),
        ('dining_room', 'restaurants', 1, 38)]
b2_df = pd.DataFrame(data,
                     columns=['room_name', 'room_type', 'room_count', 'people_count'],
                    )
b2_df

# %%
b2_dict = b2_df.to_dict(orient='records')
b2_dict

# %%
room_list = [Room(**x) for x in b2_dict]
b2_water = 0
for room in room_list:
    b2_water += getWater(room.room_type, room.room_count, room.people_count)
b2_water

# %%
data = [('gym', 'gyms', 1, 10),
        ('fronton', 'gyms', 1, 25)]
b3_df = pd.DataFrame(data,
                     columns=['room_name', 'room_type', 'room_count', 'people_count'],
                    )
b3_df

# %%
b3_dict = b3_df.to_dict(orient='records')
b3_dict

# %%
room_list = [Room(**x) for x in b3_dict]
b3_water = 0
for room in room_list:
    b3_water += getWater(room.room_type, room.room_count, room.people_count)
b3_water

# %%
data = [('dwellings', 'single_family_dwellings', 4, 4),
        ('restaurant', 'restaurants', 1, 20), 
        ('hostel', 'hostel', 1, 15)]
b4_df = pd.DataFrame(data,
                     columns=['room_name', 'room_type', 'room_count', 'people_count'],
                    )
b4_df

# %%
b4_dict = b4_df.to_dict(orient='records')
b4_dict

# %%
room_list = [Room(**x) for x in b4_dict]
b4_water = 0
for room in room_list:
    b4_water += getWater(room.room_type, room.room_count, room.people_count)
b4_water

# %%
#Total water consumption for four (4) buildings in the disctrict
total_water = b1_water + b2_water + b3_water + b4_water
total_water

# %%
c = 4186       #specific heat of water at J/kg-K
hwt = 60        #hot water temperature requirement at degC

#calculating demand in Joules, Q = m*c*deltaT*no.days

demand = pd.DataFrame()
demand['calendar_days'] = brussels_df['calendar_days'][0:12]
demand['mwt'] = [9,10,10,11,13,15,17,17,16,14,11,10]
demand['b1'] = b1_water*c*(hwt - demand['mwt'])*demand['calendar_days']
demand['b2'] = b2_water*c*(hwt - demand['mwt'])*demand['calendar_days']
demand['b3'] = b3_water*c*(hwt - demand['mwt'])*demand['calendar_days']
demand['b4'] = b4_water*c*(hwt - demand['mwt'])*demand['calendar_days']
demand['total'] = demand['b1'] + demand['b2'] + demand['b3'] + demand['b4']
demand

# %% [markdown]
# # Calculation of Solar Thermal Area based on available solar thermal brands

# %%
data = [('AP-30', 2.005, 2.195, 2.83, 0.687, 1.505, 0.0111),
        ('Promatop 1.5', 1.51, 1.01, 1.34, 0.76, 4.54, 0.012), 
        ('Promatop 2.6', 2.005, 2.196, 2.83, 0.687, 1.505, 0.0111)
#additional brands can be added here   
       ]

solar_df = pd.DataFrame(data,
                     columns=['model', 'length', 'width', 'aperture_area', 'tau_alpha', 'k1', 'k2',],
                    )
solar_df

# %%
solar_dict = solar_df.to_dict(orient='records')
solar_dict

# %%
solar_dict[0]['model']

# %%
import math

#latitude - latitude of the palce
#declination at worst day = -23.45 degrees
#solar altitude at noon = 23.284 degrees

#col_hor = horizontal dimension (size) of the collector

def distancing(slope_collector, slope_roof, col_hor):
    #conversion to radians
#    declination = -23.45 * math.pi / 180
    altitude = 23.284 * math.pi / 180
#    if -90 <= lat <= 90: 
#        lat = lat * math.pi / 180
    if 0 <= slope_collector <= 90: 
        slope_collector = slope_collector * math.pi / 180
    if 0 <= slope_roof <= 90:
        slope_roof = slope_roof * math.pi / 180

    #security factor, s 
    if slope_collector == slope_roof:
        s = 1
    else:
        s = 1.25
        
    d1 = col_hor * math.sin(slope_collector - slope_roof) / math.tan(altitude + slope_roof)
    d2 = col_hor * math.cos(slope_collector - slope_roof)
    d = s * (d1 + d2)

    return d
    

# %%
distancing(45, 35, 2.196)

# %%

#roof_hor = horizontal dimension (size) of the roof
#roof_ver = vertical dimension (size) of the roof
#col_hor = horizontal dimension (size) of the collector
#col_hor = vertical dimension (size) of the collector
irradiance_area = 0

def no_collector(roof_hor, roof_ver, col_hor, col_ver):
    roof_area = roof_hor * roof_ver
    col_area = col_hor * col_ver
    
    columns = roof_hor // col_ver
    rows = roof_ver // col_hor
    total_no = columns * rows
    global irradiance_area
    irradiance_area = total_no * col_area
    
    return print(f'The total number of solar panels is {total_no}.'), print(f'The total solar panel area is {irradiance_area} m2.')
    

# %%
no_collector(17, 6, 2.196, 2.005)

# %% [markdown]
# # Start Calculation

# %%
# Choose the the year for consideration
year = 2019
calcdf = brussels_df[brussels_df['year'] == year]
calcdf.reset_index(inplace=True)
calcdf

# %%
calcdf = calcdf[['year', 'month', 'global_horizontal_irradiation',
#       'global_irradiation_optimum_angle', 'direct_normal_irradiation',
#       'diffuse_global_ratio', 
                'outdoor_temperature', 'date', 'calendar_days',
                'business_days'
               ]].copy()


# %%
#conversion from kWh/m2/mo to J/m2/day : 1kWh(1000Wh/1kWh)(3600s/1h) = 3600000 J

calcdf['H'] = (calcdf['global_horizontal_irradiation']/calcdf['calendar_days'])*3600000     #units in J/m2/day
calcdf['L'] = demand['total']               #units in J
calcdf

# %%
fr = 0.94      #heat removal factor
model = 0       #from solar_df
tref = 100      #reference temperature at 100 degC
storage = 75        #solar water storage
thot = 60           #required hot water

calcdf['mwt'] = demand['mwt']

# Calculate X
calcdf['X'] = irradiance_area*fr*solar_df.loc[model, 'k1']*(tref - calcdf['outdoor_temperature'])*calcdf['calendar_days']*24*3600/calcdf['L']
calcdf["X'"] = calcdf['X']*(11.6 + 1.18*thot + 3.86*calcdf['mwt'] - 2.32*calcdf['outdoor_temperature'])/(100 - calcdf['outdoor_temperature'])

#calculate Y
calcdf['Y'] = irradiance_area*fr*solar_df.loc[model, 'tau_alpha']*calcdf['H']*calcdf['calendar_days']/calcdf['L']


calcdf['f'] = 1.029*calcdf['Y'] - 0.065*calcdf["X'"] - 0.245*(calcdf['Y']**2) + 0.0018*calcdf["X'"]  + 0.0215*(calcdf['Y']**3)

calcdf



# %%
sns.set_theme(style='whitegrid')
ax = sns.barplot(x='month', y='f', data=calcdf)
ax.set(xlabel='Months', ylabel='Solar Fraction')



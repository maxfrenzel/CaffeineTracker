import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np

pathname = '/Users/mff209/Documents/CaffeineTracker/'
filename = pathname + 'Coffee.csv'

# Set a timeframe for plots
t_initial = datetime.datetime(2014, 5, 2, 0, 0)
t_final = datetime.datetime(2016, 6, 30, 0, 0)

# What to plot? All (1), Average (2), Maximum Day (3)
plot_type = 3
# Save plot?
save_plot = True

# List of caffeine content of different drinks (in mg)
# [none, single espresso, double espresso, double espresso decaf, 
#  filter, coldbrew, matcha, other tea]
caffeine_list = [0.0,70.0,140.0,10.0,175.0,210.0,70.0,50.0]

# Biological half life time of caffeine (in minutes)
half_life = 5.0*60.0
# Variance of Gaussian modelling caffeine entering bloodstream
sigma = 60

# Temporal resolustion
resolution = 5
dt = datetime.timedelta(minutes=resolution)

# Decay factor
decay_factor = (0.5)**(resolution/half_life)

# Initialise empty list
Events = []

# Read events from file, giving each event a time and a type
with open(filename, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    
    reader.next()
    reader.next()
    reader.next()
    
    for row in reader:
        for i in range(len(row)-1):
            if row[i+1] == '"1"':
                CType = i+1
                break
            else: 
                CType = "none"
        
        Events.append([datetime.datetime.strptime(row[0], '"%d %B %Y %H:%M:%S %Z"'), CType])

# Set starting time and initialise timestamp and caffeineLevel lists
t_start = Events[0][0]
time = t_start + dt

timestamps = [t_start]
#if Events[0][1] != "none":
#    caffeineLevel = [0]
#else:
caffeineLevel = [0]
    
event_index = 0

# List to store events until all their caffeine is in bloodstream
past_events = []
    
while time < (Events[-1][0] + datetime.timedelta(minutes=300)):
    
    new_caffeine_level = caffeineLevel[-1] * decay_factor

    if event_index < len(Events) and time > Events[event_index][0]:
        if Events[event_index][1] != "none":
            
            # Create Gaussian that will model caffeine entering bloodstream
            gaussian = [np.exp(-(k*resolution-30)**2/sigma) for k in range(25)]
            # Normalise
            gaussian = [x * caffeine_list[Events[event_index][1]]/sum(gaussian) for x in gaussian]
            
            # Add Gaussian to list of past events
            past_events.append(gaussian)
            
        event_index += 1
        
    # Add caffeine for all still outstanding past events
    add_caffeine = 0.0
    for c in past_events:
        add_caffeine += c[0]
        del c[0]
        # Remove event if this was the last entry
        if c == []:
            past_events.remove(c)
                    
    new_caffeine_level += add_caffeine
    
    caffeineLevel.append(new_caffeine_level)
    timestamps.append(time)
    #print new_caffeine_level
    
    time += dt
    
# Remove data outside chosen timeframe
#initial_index = [timestamps.index(t) for t in timestamps \
#                if ((t > t_initial) and (t < t_final))]
try:
    initial_index = next(timestamps.index(t) for t in timestamps if (t > t_initial))
except:
    initial_index = 0
try:
    final_index = next(timestamps.index(t) for t in timestamps if (t > t_final))
except:
    final_index = -1
timestamps = timestamps[initial_index:final_index]
caffeineLevel = caffeineLevel[initial_index:final_index]
    
# Daily average
time = datetime.datetime(2015, 1, 1, 0, 0)

timestamps_average = [time]
caffeine_average = []

for k in range(int(1440/resolution)-1):
    time += dt
    timestamps_average.append(time)
    
for time in timestamps_average:
    # Times in total list
    occurences = [t for t in timestamps if t.time().replace(second=0) == time.time()]
    caffeine_list = [caffeineLevel[timestamps.index(t)] for t in occurences]
    
    if len(occurences) != 0:
        caffeine_average.append(sum(caffeine_list)/len(occurences))
        
# Most caffeinated day
peak_index = caffeineLevel.index(max(caffeineLevel))
peak_time = timestamps[peak_index]
delta_t = peak_time.time().hour * 60 + (peak_time.time().minute)
delta_index = int(delta_t/resolution)
max_day_first_index = peak_index - delta_index
max_day_last_index = max_day_first_index + int(60*24/resolution)
max_day_times = timestamps[max_day_first_index:max_day_last_index]
max_day_caffeine = caffeineLevel[max_day_first_index:max_day_last_index]

    
# Convert to arrays
if plot_type == 1:
    x = np.array(timestamps)
    y = np.array(caffeineLevel)
elif plot_type == 2:
    x = np.array(timestamps_average)
    y = np.array(caffeine_average)
elif plot_type == 3:
    x = np.array(max_day_times)
    y = np.array(max_day_caffeine)

with plt.style.context('fivethirtyeight'):
#with plt.xkcd():
    plot = plt.plot(x,y)
    plt.fill_between(x,0,y, alpha=0.2)
    if plot_type == 1:
        plt.title('Caffeine between ' + timestamps[0].strftime("%d %B %Y")\
                    + ' and ' + timestamps[-1].strftime("%d %B %Y"))
    elif plot_type == 2:
        plt.title('Average caffeine between ' + timestamps[0].strftime("%d %B %Y")\
                    + ' and ' + timestamps[-1].strftime("%d %B %Y"))
    elif plot_type == 3:
        plt.title('Most caffeinated day: ' + peak_time.strftime("%A, %d %B %Y"))
    plt.ylabel('Caffeine (mg)')
    plt.xlabel('Time')
    plt.setp(plot, linewidth=2.0)
    plt.grid(True)
    plt.tight_layout()
    fig = plt.gcf()
    fig.set_size_inches(14, 10.5, forward=True)
    if save_plot == True:
        fig.savefig(pathname+'plot' +str(plot_type) + '.png', dpi=100)
    plt.show()
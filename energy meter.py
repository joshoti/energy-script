import datetime
print('start')
start_of_timer = datetime.datetime.now()
#from pandas import read_pickle
import pickle

year = start_of_timer.year
timer1 = (datetime.datetime.now() - start_of_timer).seconds
def rate_hours(later_date, earlier_date, upper_amount, lower_amount): # earlier === upper, later === lower
    time_difference = later_date - earlier_date
    hours = time_difference.total_seconds()/3600
    print(f"{hours:.2f} Hours")
    amount = upper_amount - lower_amount
    rate = round(amount/hours, 2)
    time_left = round(lower_amount/rate, 2)
    print(f"{rate} kW per hour in the past {time_difference.__str__()}")
    print(f"At current rate {time_left} hours remaining")
    time_left_datetime_format = datetime.timedelta(hours=time_left)
    print(f'Terminating at: {(time_left_datetime_format + later_date).ctime()[:19]}\n')

timer2 = (datetime.datetime.now() - start_of_timer).seconds
def printlog(log):
    """Print saved log, if not empty"""
    if len(log) > 0:
        for key,value in log.items(): print(key,value)

def meter_cycler(log, s_all, s_20, n, index, auto=False):
    difference = -1 if auto else 1
    k = index+difference
    later_date = s_20[index]
    lower_amount, lower_hour, lower_month, lower_day, lower_month = later_date
    later_full_date = datetime.datetime(year, lower_month, lower_day, lower_hour, lower_month)
    while k <= n:        
        earlier_date = s_20[k]
        upper_amount, upper_hour, upper_minute, upper_day, upper_month = earlier_date
        temp_amount, *temp_info = s_20[k-difference]
        if auto:
            if upper_amount < temp_amount: break
        else:
            if upper_amount > temp_amount: break
        earlier_full_date = datetime.datetime(year, upper_month, upper_day, upper_hour, upper_minute)
        print(f'\nIndex {k}:', end='     ')
        rate_hours(later_full_date, earlier_full_date, upper_amount, lower_amount) if auto else rate_hours(earlier_full_date, later_full_date, lower_amount, upper_amount)
        k+=difference
    
def meter(log, s_all, s_20, n, auto=False):
    """Calculates rate of consumption and length of time between readings"""    
    if auto: # IF a function calls this function
        meter_cycler(log, s_all, s_20, n, n, auto)
        return n, log
    
    printlog(log)
    while True:
        upper_reading_is_entered = input('\nHELP: ["q" to quit ] ("n" to enter value) ["p" to see log]\nEnter desired index:  ')
        if upper_reading_is_entered == "q": break
        if upper_reading_is_entered == "p": printlog(log); continue
        elif upper_reading_is_entered == "n":
            n,log = elog(log, s_all, s_20, n)
            return n, log
        meter_cycler(log, s_all, s_20, n, int(upper_reading_is_entered))

        if len(log) < 6: log = view_tail(s_20,n)
    return n, log
timer3 = (datetime.datetime.now() - start_of_timer).seconds

def interpolate_rate(amount, rate_info, full_date):
    if type(rate_info) == tuple:
        name, rate = rate_info
        print(f'\nUsing {name} at {rate}')
    else:
        rate = rate_info
    time_left = round(amount/rate, 2)
    time_left_datetime_format = datetime.timedelta(hours=time_left)    
    if time_left > 24:
        day = time_left//24
        hour = time_left-(day*24)
        print(f"{day} day(s) : {hour:.2f} hour(s) from {full_date.ctime()[:19]}\nTerminating at: {(time_left_datetime_format + full_date).ctime()[:19]}\n")
    else:
        print(f"{time_left} hours from {full_date.ctime()[:19]}\nTerminating at: {(time_left_datetime_format + full_date).ctime()[:19]}\n")
            
def interpolate(log, s_all, s_20, n):
    """Use different rates to observe consumption of credit"""
    printlog(log)
    meter_reading = input('Enter desired index? ["n" to enter value] ')
    if meter_reading.isnumeric():
        row_of_data = log[int(meter_reading)]
        amount,hour,minute,day,month = row_of_data
    elif meter_reading == 'n':
        reading_entry = input("\nPrevious:\nAmount (24)Hour Mintue Day Month\n").split()
        hour,minute,day,month = map(int,reading_entry[1:])
        amount = float(reading_entry[0])
        s_all[n+1] = [amount,hour,minute,day,month]
        s_20[n+1] = [amount,hour,minute,day,month]
        n+=1
        if len(log) < 6: log = view_tail(s_20,n)   
    full_date = datetime.datetime(2022,month,day,hour,minute)
    day_rate, overnight_rate = 2.0, 2.81
    average_rate = round((day_rate + overnight_rate)/2 ,2)
    rates = [("Day Rate", day_rate), ("Night Rate", overnight_rate), ("Average Rate", average_rate), ]
    for rate_info in rates:
        interpolate_rate(amount, rate_info, full_date)
    while True:        
        rate = input('Rate: ["q" to quit] ("p" to see log) \n')
        if rate == 'q': break
        if rate == 'p': printlog(log); continue
        interpolate_rate(amount, float(rate), full_date)
    return n, log

def elog(log, s_all, s_20, n):
    """Enters new reading"""
    printlog(s_20)
    repeat = input("How many values do you want to add ")
    repeat = 1 if repeat == '' else int(repeat)
    for _ in range(repeat):
        reading_entry = input(f"\nEntry {_+1} out of {repeat}:\nAmount (24)Hour Mintue Day Month\n").split()
        if len(reading_entry) == 0: break
        elif reading_entry[-1].lower() == 'n': reading_entry.pop(); reading_entry.extend(s_20[n][-2:]); reading_entry[-2] += 1 # Fills the next date if it sees n (next date)
        elif 3 <= len(reading_entry) < 5: reading_entry.extend(s_20[n][len(reading_entry)-5:])  # Fills the appropriate date if entry is incomplete
        hour,minute,day,month = map(int,reading_entry[1:])
        amount = float(reading_entry[0])
        s_all[n+1] = [amount,hour,minute,day,month]
        s_20[n+1] = [amount,hour,minute,day,month]
        n+=1
        n, log = meter(log, s_all, s_20, n, True)
    if len(log) < 6: log = view_tail(s_20,n); return n, log
    return n, log
timer4 = (datetime.datetime.now() - start_of_timer).seconds
def writeoff(s_all,n,axes):
    """Updates report by rewriting source file"""
    print('Writing off. Please wait...')
    writeoff_timer = datetime.datetime.now()
    from pandas import DataFrame
    state1_time = (datetime.datetime.now() - writeoff_timer).seconds
    
    df = DataFrame(s_all).T # Turns saved log to a dataframe
    final = df.set_axis(axes, axis='columns') # Column names are entered
    state2_time = (datetime.datetime.now() - writeoff_timer).seconds
    conv1_time = datetime.datetime.now()
    final.to_pickle("energy meter report.pickle")
    pickle_time = (datetime.datetime.now() - conv1_time).seconds
    conv2_time = datetime.datetime.now()
    final.to_excel("energy meter report.xlsx")
    excel_time = (datetime.datetime.now() - conv2_time).seconds
    conv3_time = datetime.datetime.now()
    final.to_csv("energy meter report.csv")
    csv_time = (datetime.datetime.now() - conv3_time).seconds
    state3_time = (datetime.datetime.now() - writeoff_timer).seconds
    print(f"\nVery Successful!\nImport Time: {state1_time}\nProcessing Time:{state2_time-state1_time}\nConversion Time:{state3_time-state2_time}\nFull Time:{state3_time}")
    print(f"\nConversion Breakdown\nPickle: {pickle_time} \nExcel: {excel_time} \nCSV: {csv_time}\n")
    
def view_tail(s_20,n):
    """Returns the last 5 entries"""
    tail = {k:v for k,v in s_20.items() if k > n-5}
    return tail
timer5 = (datetime.datetime.now() - start_of_timer).seconds
def remove_log(log, s_all, s_20, n):
    """Removes last entry if index isn't specified"""
    print(f'{n}: {s_all[n]} Removed!\n')
    s_all.pop(n)
    s_20.pop(n)
    if len(log) < 6: log = view_tail(s_20,n-1); return n-1, log
    return n-1, log

def watts_forecast(seconds, appliance):
    watts_consumed = 10
    time_in_minutes = watts_consumed * 60 / seconds
    time_in_hours = time_in_minutes * 60
    print(f"{time_in_minutes:.2f} W/minutes.  {time_in_hours/1000:.2f} kW/hours")
    watts_report[appliance] = f"{time_in_hours/1000:.2f}"
    
#data = read_pickle(r'C:\Users\Joshua\Documents\energy meter report.pickle')
timer6 = (datetime.datetime.now() - start_of_timer).seconds
with open('C:/Users/Joshua/Documents/energy meter report.pickle', 'rb') as pickled_file:
    data = pickle.load(pickled_file)
timer7 = (datetime.datetime.now() - start_of_timer).seconds
no_of_rows = len(data)
saved, saved_20, watts_report = {}, {}, {}
for row in range(no_of_rows): # Loops through dataframe and saves it in dictionary
    row_of_data = list(data.iloc[row])
    row_of_data[1:] = map(int,row_of_data[1:]) # Make dates to be integer values (eg from 20.0/3.0/2022.0 => 20/3/2022)
    saved[row+1] = row_of_data # Complete dictionary for writing out to pickle, csv, excel docs
    if no_of_rows - row < 21: saved_20[row+1] = row_of_data # Makes dictionary with 20 items for use in code
timer8 = (datetime.datetime.now() - start_of_timer).seconds	
n = sorted(saved.keys())[-1]
axes = list(data.columns)
saved_5 = view_tail(saved,n)
loglist = saved_5

startup_time = (datetime.datetime.now() - start_of_timer).seconds
print(f'stopped: It took {startup_time} second(s)')
timer9 = (datetime.datetime.now() - start_of_timer).seconds
with open ('energy meter start ups.txt', 'r') as file:
    previous_startup_time = file.readlines()[-1].strip()
    # previous_startup_time = file.readlines()[-1][:2]

print(f'Previous Start up time was {previous_startup_time} second(s)\n')
timer10 = (datetime.datetime.now() - start_of_timer).seconds
with open ('energy meter start ups.txt', 'a') as file:
    file.write(f'{startup_time}\n')
    # file.write(f'{startup_time} - {datetime.datetime.now().__str__()[:19]}\n')
    del startup_time, previous_startup_time # Releasing memory
    # del startup_time, previous_startup_time, start_of_timer # Releasing memory
timer11 = (datetime.datetime.now() - start_of_timer).seconds
print(f"1: {timer1}  2: {timer2}  3: {timer3}\n4: {timer4}  5: {timer5}  6: {timer6}\n7: {timer7}  8: {timer8}  9: {timer9} \n10: {timer10}  11: {timer11}")
while True:
    """The actual program"""
    que = input("Meter / Interpolate / Log(-F) / Toggle / Enter / Remove / Writeoff: ").lower()
    if que.startswith('m'): n,loglist = meter(loglist, saved, saved_20, n)
    elif que.startswith('i'): n,loglist = interpolate(loglist, saved, saved_20, n)
    elif que.startswith('e'): n,loglist = elog(loglist, saved, saved_20, n)
    elif que.startswith('l'):
        if que == 'lf': printlog(saved)
        else: printlog(loglist)
    elif que.startswith('t'):
        if len(loglist) < 6: loglist = saved_20
        else: saved_5 = view_tail(saved_20,n); loglist = saved_5
    elif que.startswith('r'): n, loglist = remove_log(loglist, saved, saved_20, n)
    elif que.startswith('w'): writeoff(saved, n, axes)
    elif que.startswith('q'): print('Over and Out!'); break


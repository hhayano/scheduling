#!/usr/bin/env python

import xlrd # For parsing excel sheets
import os

err = open("scheduling_error.txt", "w")

# Timeframe will contain:
#  1. start time of the timeframe
#  2. end time of the timeframe
#  3. day of the timeframe
# - 0 will represent Sunday, 1 = Monday, ... 6 = Saturday for the weekday
# - Military time will be used to remain clear of confusion
# - allow the days to wrap around so that it makes referencing easier
class Timeframe(object):
    def __init__(self, start, end, day):
        self.start_time = float(start)
        self.end_time = float(end)
        if day == -1:
            self.weekday = 6
        elif day == 7:
            self.weekday = 0
        else:
            self.weekday = day
        self.len = self.end_time - self.start_time

    def __eq__(self, other):
        if self.start_time == other.start_time and self.end_time == other.end_time and self.weekday == other.weekday:
            return True
        else:
            return False

# Shifts will contain:
#  1. timeframe of the shift
#  2. amount of workers needed (spots available)
#  3. list of workers assigned to the shift
# - Shifts will be used for both the main schedule and the schedule requests
# - For midshifts/desk shifts, the last element of the list of workers will be on drawer
# - For Schedule Requests
#   - Number of workers for shifts will always be 0
#   - List of workers will be empty
class Shift(object):

    # For the initialization of a Shift, we will assume that no workers have been assigned
    #   to the shift. Allow the days to wrap around
    def __init__(self, time, num_workers):
        self.time_frame = time
        self.num_spots = num_workers
        self.workers = []

    # provides a way to check if the shift described by *other* is still available
    # this is used by the Schedule.has() to check if a Schedule object has a shift
    #   specified by *other* that is still open
    def equal(self, other):
        if self.time_frame == other.time_frame:
            return True
        else:
            return False



# Schedule will contain:
#  1. minimum hours
#  2. maximum hours
#  3. list of shifts (midshifts, desk shifts, and extra shifts)
#  4. number of workers
# - desk shifts and extra shift will be passed into the constructor as those shifts will
#   vary weekly (Single staffed shifts for desk shifts)
# - desk shifts will be represented by whole hours, effectively ignoring the extra 15
#   minutes at the start of the shift for now.
class Schedule(object):

    # Initialize a new Schedule. We want to be able to change desk shifts (single staff
    #   shifts) and extra shifts
    def __init__(self, min_hours, max_hours, midshifts, desk_shifts, extra_shifts, num_workers):
        self.min_hours = float(min_hours)
        self.max_hours = float(max_hours)
        self.shifts = []
        self.shifts.append(midshifts)
        self.shifts.append(desk_shifts)
        self.shifts.append(extra_shifts)
        self.num_workers = num_workers

    # Provides a way to check if a certain shift is still available
    # Returns the shift if it is available, return None if not
    def has(self, target_shift):
        for shift_type_list in self.shifts:
            if shift_type_list != None:
                for shift in shift_type_list:
                    if shift.equal(target_shift) == True and shift.num_spots > 0:
                        return shift

        return None


# Requests will contain:
#  1. list of midshift preferences
#  2. list of preferred shifts
#  3. list of available shifts
#  4. list of secondary choice shifts
#  5. midshift (yes/no)
#  6. number of requested hours
# - Every Worker will have a Schedule Request
# - Items 1 through 4 will be represented as a list of shifts in that order
# - Priority will be represented by the order that of the requests in a list
class Request(object):

    def __init__(self, midshift, preferred, available, secondary, midshift_pref, num_hours):
        self.shifts = []
        self.shifts.append(midshift)
        self.shifts.append(preferred)
        self.shifts.append(available)
        self.shifts.append(secondary)
        self.mid_pref = midshift_pref
        self.num_hours = num_hours


# Worker will contain:
#  1. name
#  2. priority
#  3. schedule request
#  4. number of assigned hours
#  5. shifts they are assigned
#  6. assignment flag that aids in the scheduling of the shifts
class Worker(object):

    # For the initialization of a Worker, we will assume that they have no shifts assigned
    #   to them
    def __init__(self, name, priority, request):
        self.name = name
        self.priority = priority
        self.request = request
        self.assigned_hours = 0.0
        self.assigned_shifts = []
        self.assignment_flag = True

# Helper function to invalidate the shifts that overlap with the timeframe specified for
#  a given worker
def invalidate_shifts(times, worker):
    if times.len == 0:
        return

    for shift_list in worker.request.shifts:
        if shift_list != None:
            for shift in shift_list:
                if times.weekday == shift.time_frame.weekday:
                    if times.start_time >= shift.time_frame.start_time and times.start_time < shift.time_frame.end_time:
                        shift_list.remove(shift)
                    elif times.end_time <= shift.time_frame.end_time and times.end_time > shift.time_frame.start_time:
                        shift_list.remove(shift)

# Helper function to assign shifts
# Assume that shift is the shift in the main schedule
def assign_shift(worker, shift):
    # Make changes to the shift to indicate that the worker has been assigned to it
    shift.num_spots -= 1
    shift.workers.append(worker)

    # Make changes to the worker to indicate that the shift has been assigned to the
    #  worker
    invalidate_shifts(shift.time_frame, worker)
    worker.assigned_shifts.append(shift)
    worker.assigned_hours += shift.time_frame.len

# Assigns midshifts to the people that need to get midshifts
def assign_midshift(main_sched, workers):

    num_midshift = 0
    for shift in main_sched.shifts[0]:
        num_midshift += shift.num_spots

    workers_left = main_sched.num_workers

    # First give shifts to all the people that want midshifts
    for indiv in workers:
        if num_midshift >= workers_left:
            break
        if indiv.request.mid_pref == True and num_midshift > 0:
            # If a worker wants a midshift, go through the midshift preferences
            for midshift in indiv.request.shifts[0]:
                avail_midshift = main_sched.has(midshift)
                if avail_midshift != None:
                    assign_shift(indiv, avail_midshift)
                    num_midshift -= 1
                    indiv.assignment_flag = False
                    invalid_time1 = Timeframe(6, 12, avail_midshift.time_frame.weekday)
                    invalid_time2 = Timeframe(21, 24, avail_midshift.time_frame.weekday-1)
                    invalidate_shifts(invalid_time1, indiv)
                    invalidate_shifts(invalid_time2, indiv)
                    break
                else:
                    #print(indiv.name + " " + str(midshift.time_frame.weekday))
                    pass

    # Second give shifts to all the people that need to have midshifts
    if num_midshift > 0:
        offset = main_sched.num_workers - num_midshift
        for indiv in workers[offset:]:
            for midshift in indiv.request.shifts[0]:
                avail_midshift = main_sched.has(midshift)
                if avail_midshift != None:
                    assign_shift(indiv, avail_midshift)
                    num_midshift -= 1
                    indiv.assignment_flag = False
                    break

    if num_midshift != 0:
        err.write("ERROR: Midshift assignment failure - not all midshifts assigned\n")
        return 1


# Parsing standardized excel files
# Takes in the file name and optionally a sheet name (Default will be the first sheet)
def excel_parse(file_name, sheet_name):
    # First get the sheet with the schedule request
    workbook = xlrd.open_workbook(file_name)
    worksheet = None
    if sheet_name == None:
        worksheet = workbook.sheet_by_index(0)
    else:
        worksheet = workbook.sheet_by_name(sheet_name)

    # Gather simple data
    name = worksheet.cell(0,1).value
    requested_hours = worksheet.cell(0,5).value
    midshift_pref_str = worksheet.cell(9,4).value
    midshift_pref_str = midshift_pref_str.lower()
    midshift_pref = False
    if midshift_pref_str == "yes":
        midshift_pref = True

    # Gather midshift preferences
    midshift_list = [Shift(23.75, 6, None, 0) for i in range(7)]
    for i in range(1, worksheet.ncols):
        index = int(worksheet.cell(2,i).value)-1
        midshift_list[index].weekday = i-1


    # Create the worker instance with corresponding request
    sched_request = Request(midshift_list, None, None, None, midshift_pref, requested_hours)
    worker = Worker(name, None, sched_request)

    return worker

# Parses excel schedule for list of workers in priority order
def excel_worker_list(file_name, excluded_file):

    # Get worker cells from the file
    workbook = xlrd.open_workbook(file_name)
    worksheet = workbook.sheet_by_index(0)
    workers = worksheet.col_slice(9)

    # Get list of names that are included in the file, but not counted as workers
    excludedfile = open(excluded_file, "r")
    excludedlist = excludedfile.read().splitlines()

    workerlist = []
    count = 1
    # Create list, adding workers only if they are actually working
    for worker in workers:
        if worker.value not in excludedlist:
            workerlist.append(Worker(worker.value, count, None))
            count += 1

    return workerlist

# To test
def midshift_creation(pref_list):
    shift_list = []
    for i in pref_list:
        time = Timeframe(0,6,i)
        shift = Shift(time, 0)
        shift_list.append(shift)
    return shift_list

def haji_test():
        #test_worker = excel_parse("request.xls", None)
    midshift_list = []
    midshift_list.append([6, 5, 0, 2, 1, 4, 3]) #0
    midshift_list.append([5, 2, 1, 6, 3, 0, 4]) #1
    midshift_list.append([1, 5, 3, 2, 4, 6, 0]) #2
    midshift_list.append([4, 3, 6, 1, 0, 2, 5]) #3
    midshift_list.append([2, 6, 5, 3, 1, 4, 0]) #4
    midshift_list.append([0, 6, 1, 5, 4, 2, 3]) #5
    midshift_list.append([0, 3, 5, 4, 1, 2, 6]) #6
    midshift_list.append([0, 6, 3, 4, 2, 1, 5]) #7
    midshift_list.append([4, 5, 0, 2, 6, 1, 3]) #8
    midshift_list.append([6, 2, 3, 4, 1, 5, 0]) #9
    midshift_list.append([1, 6, 3, 0, 2, 4, 5]) #10
    midshift_list.append([2, 5, 0, 4, 3, 6, 1]) #11
    midshift_list.append([6, 2, 5, 1, 0, 4, 3]) #12
    midshift_list.append([4, 2, 0, 1, 3, 6, 5]) #13
    midshift_list.append([5, 1, 6, 3, 0, 2, 4]) #14
    midshift_list.append([6, 3, 4, 1, 2, 0, 5]) #15
    midshift_list.append([6, 0, 2, 3, 5, 4, 1]) #16
    midshift_list.append([2, 6, 4, 1, 5, 0, 3]) #17
    midshift_list.append([0, 2, 3, 5, 6, 4, 1]) #18
    midshift_list.append([4, 5, 6, 1, 2, 0, 3]) #19
    midshift_list.append([1, 3, 4, 6, 5, 2, 0]) #20
    midshift_list.append([3, 5, 2, 1, 4, 6, 0]) #21
    midshift_list.append([5, 2, 3, 1, 4, 0, 6]) #22
    midshift_list.append([1, 2, 6, 4, 5, 0, 3]) #23
    midshift_list.append([5, 3, 1, 2, 0, 4, 6]) #24
    midshift_list.append([3, 0, 6, 2, 5, 1, 4]) #25
    midshift_list.append([4, 6, 3, 5, 0, 2, 1]) #26
    midshift_list.append([0, 4, 1, 2, 5, 3, 6]) #27

    mid_pref_list = []
    mid_pref_list.append(1)
    mid_pref_list.append(1)
    mid_pref_list.append(1)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(1)
    mid_pref_list.append(1)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(1)
    mid_pref_list.append(1)
    mid_pref_list.append(1)
    mid_pref_list.append(1)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)
    mid_pref_list.append(0)

    test_worker_list = []
    for i in range(28):
        midshifts = midshift_creation(midshift_list[i])
        test_request = Request(midshifts, None, None, None, mid_pref_list[i], 12)
        test_worker = Worker(str(i), i, test_request)
        test_worker_list.append(test_worker)

    test_timeframe_list = []
    for i in range(7):
        test_timeframe = Timeframe(0,6,i)
        test_timeframe_list.append(test_timeframe)

    sched_midshift_list = []
    for times in test_timeframe_list:
        sched_midshift = Shift(times, 2)
        sched_midshift_list.append(sched_midshift)

    test_main_sched = Schedule(12, 20, sched_midshift_list, None, None, 28)

    assign_midshift(test_main_sched, test_worker_list)

    haji_test_output = open("test/haji_test", "w")
    for shift in test_main_sched.shifts[0]:
        haji_test_output.write("The people working on " + str(shift.time_frame.weekday) + " is/are: \n")
        for worker in shift.workers:
            haji_test_output.write(worker.name + '\n')
        haji_test_output.write("")



    # parse requests
    # parse shifts that need to be filled
    # assign midshifts
    # assign desk shifts
    # assign extra shifts

def worker_test():
    workers = excel_worker_list("schedules/Week 2.xlsx", "excluded.txt")
    workerfile = open("test/workertest.txt", "w")
    for worker in workers:
        workerfile.write("Name: " + worker.name + "  Priority: " + str(worker.priority) + "\n")

def run_tests():
    try: 
        os.makedirs("test/")
    except OSError:
        if not os.path.isdir("test/"):
            raise

    worker_test()
    haji_test()

def main():
    run_tests()



if __name__ == "__main__":
    main()

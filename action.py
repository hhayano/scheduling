#!/usr/bin/env python

import xlrd # For parsing excel sheets
import os
import object

err = open("error_action.txt", "w")

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
                    invalid_time1 = object.Timeframe(6, 12, avail_midshift.time_frame.weekday)
                    invalid_time2 = object.Timeframe(21, 24, avail_midshift.time_frame.weekday-1)
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
                    invalid_time1 = object.Timeframe(6, 12, avail_midshift.time_frame.weekday)
                    invalid_time2 = object.Timeframe(21, 24, avail_midshift.time_frame.weekday-1)
                    invalidate_shifts(invalid_time1, indiv)
                    invalidate_shifts(invalid_time2, indiv)
                    break

    if num_midshift != 0:
        err.write("ERROR: Midshift assignment failure - not all midshifts assigned\n")
        return 1

def assign_deskshifts(main_sched, workers):
    # First count the number of deskshifts we need to assign
    num_deskshifts = 0
    for shift in main_sched:
        num_deskshifts += shift.num_spots

    # First assign 6 hours to people that didn't get midshifts
    for indiv in workers:
        error_code = assign_deskshift_helper(main_sched, indiv, 1, 3, 6)
        if error_code != 0:
            err.write("ERROR: Desk Shift assignment failure - initial 6hr block not assigned properly\n")
        else:
            num_deskshifts -= 2
            indiv.assignment_flag = False

    for indiv in workers:
        if indiv.assignment_flag == False:
            indiv.assignment_flag = True
        else:
            err.write("ERROR: Desk Shift assignment failure - initial 6hr block not assigned properly\n")

    # Second assign 3 hours in rotation until A) everyone has requested hours OR B) run
    #  out of desk shifts
    # A)
    workers_left = main_sched.num_workers
    while workers_left < num_deskshifts and workers_left > 0 and num_deskshifts > 0:
        for indiv in workers:
            if num_deskshifts <= 0:
                break
            error_code = assign_deskshift_helper(main_sched, indiv, 1, 3, indiv.assigned_hours+3)
            if error_code != 0:
                err.write("ERROR: Desk Shift assignment failure - initial 6hr block not assigned properly\n")
            else:
                if indiv.assigned_hours > indiv.request.num_hours:
                    indiv.assignment_flag = False
                    workers_left -= 1
                    num_deskshifts -= 1






def assign_deskshift_helper(schedule, worker, shift_list_start, shift_list_end, target_hours):
    if worker.assignment_flag == False:
        return 0
    for shift_list in range(shift_list_start, shift_list_end+1):
        for deskshift in indiv.request.shifts[shift_list]:
            avail_deskshift = schedule.has(deskshift)
            if avail_deskshift != None:
                assign_shift(worker, avail_deskshift)
                if worker.assigned_hours == target_hours:
                    return 0
    return 1


# Parsing standardized excel files
# Takes in the file name and optionally a sheet name (Default will be the first sheet)
# OUTDATED!!!!!
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
    midshift_list = [object.Shift(23.75, 6, None, 0) for i in range(7)]
    for i in range(1, worksheet.ncols):
        index = int(worksheet.cell(2,i).value)-1
        midshift_list[index].weekday = i-1


    # Create the worker instance with corresponding request
    sched_request = object.Request(midshift_list, None, None, None, midshift_pref, requested_hours)
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
            workerlist.append(object.Worker(worker.value, count, None))
            count += 1

    return workerlist

# To test
def midshift_creation(pref_list):
    shift_list = []
    for i in pref_list:
        time = object.Timeframe(0,6,i)
        shift = object.Shift(time, 0)
        shift_list.append(shift)
    return shift_list

#!/usr/bin/env python

import os
import object
import action

# Create a bunch of fake midshift requests and see if the midshift assignment works
def midshift_test():
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

    # Create the list of workers that we will pass into the schedule creation function
    test_worker_list = []
    for i in range(28):
        midshifts = action.midshift_creation(midshift_list[i])
        test_request = object.Request(midshifts, None, None, None, None, None, None, mid_pref_list[i], 12)
        test_worker = object.Worker(str(i), i, test_request)
        test_worker_list.append(test_worker)

    # Create the list of midshifts that we will use for the main schedule
    test_timeframe_list = []
    for i in range(7):
        test_timeframe = object.Timeframe(0,6,i)
        test_timeframe_list.append(test_timeframe)

    sched_midshift_list = []
    for times in test_timeframe_list:
        sched_midshift = object.Shift(times, 2)
        sched_midshift_list.append(sched_midshift)

    # Create the main schedule using the list of midshift created above
    test_main_sched = object.Schedule(12, 20, sched_midshift_list, None, None, 28)

    action.assign_midshift(test_main_sched, test_worker_list)

    # Print the schedule
    haji_test_output = open("test/haji_test", "w")
    for shift in test_main_sched.shifts[0]:
        haji_test_output.write("The people working on " + str(shift.time_frame.weekday) + " is/are: \n")
        for worker in shift.workers:
            haji_test_output.write(worker.name + '\n')
        haji_test_output.write("")

def worker_test():
    workers = action.excel_worker_list("schedules/Week 2.xlsx", "excluded.txt")
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
    midshift_test()

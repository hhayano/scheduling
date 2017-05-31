#!/usr/bin/env python

err = open("scheduling_error.txt", "w")

# Shifts will contain:
#  1. start times
#  2. end times
#  3. day of the shift
#  4. amount of workers needed (spots available)
#  5. list of workers assigned to the shift
# - Shifts will be used for both the main schedule and the schedule requests
# - For midshifts/desk shifts, the last element of the list of workers will be on drawer
# - 0 will represent Sunday, 1 = Monday, ... 6 = Saturday for the weekday
# - Military time will be used to remain clear of confusion
# - For Schedule Requests
#   - Number of workers for shifts will always be 0
#   - List of workers will be empty
class Shift(object):

    # For the initialization of a Shift, we will assume that no workers have been assigned
    #   to the shift
    def __init__(self, start, end, day, num_workers):
        self.start_time = float(start)
        self.end_time = float(end)
        self.weekday = day
        self.num_spots = num_workers
        self.workers = []

    # provides a way to check if the shift described by *other* is still available
    # this is used by the Schedule.has() to check if a Schedule object has a shift
    #   specified by *other* that is still open
    def equal(self, other):
        if self.start_time == other.start_time and self.end_time == other.end_time and self.weekday == other.weekday:
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
class Schedule(object):

    # Create the list of Shifts representing midshifts
    midshifts = [Shift(23.75, 6.0, i, 2) for i in range(7)]

    # Initialize a new Schedule. We want to be able to change desk shifts (single staff
    #   shifts) and extra shifts
    def __init__(self, min_hours, max_hours, desk_shifts, extra_shifts, num_workers):
        self.min_hours = float(min_hours)
        self.max_hours = float(max_hours)
        self.desk_shifts = desk_shifts
        self.extra_shifts = extra_shifts
        self.num_workers = num_workers

    # Provides a way to check if a certain shift is still available
    # Make sure the type of shift is provided so the check is faster
    # Returns the shift if it is available, return None if not
    def has(self, target_shift, shift_type):
        if shift_type == "midshift":
            for shift in self.midshifts:
                if shift.equal(target_shift) == True and shift.num_workers > 0:
                    return shift
        elif shift_type == "desk":
            for shift in self.desk_shifts:
                if shift.equal(target_shift) == True and shift.num_workers > 0:
                    return shift
        elif shift_type == "extra":
            for shift in self.extra_shifts:
                if shift.equal(target_shift) == True and shift.num_workers > 0:
                    return shift
        else:
            err.write("ERROR: Invalid input for Schedule.has()\n")
        return None






# Requests will contain:
#  1. list of hours that the worker is not available to work
#  2. list of midshift preferences
#  3. list of preferred shifts
#  4. list of available shifts
#  5. list of secondary choice shifts
#  6. midshift (yes/no)
#  7. number of requested hours
# - Every Worker will have a Schedule Request
# - Items 1 through 5 will be represented as a list of shifts
# - Priority will be represented by the order that of the requests in a list
class Request(object):

    def __init__(self, unavailable, midshift, preferred, available, secondary, midshift_pref, num_hours):
        self.unavail = unavailable
        self.midshift = midshift
        self.pref = preferred
        self.avail = available
        self.second = secondary
        self.mid_pref = midshift_pref
        self.num_hours = num_hours

# Worker will contain:
#  1. name
#  2. priority
#  3. schedule request
#  4. number of assigned hours
#  5. shifts they are assigned
class Worker(object):

    # For the initialization of a Worker, we will assume that they have no shifts assigned
    #   to them
    def __init__(self, name, priority, request):
        self.name = name
        self.priority = priority
        self.request = request
        self.assigned_hours = 0.0
        self.assigned_shifts = []

# Helper function to assign shifts
def assign_shift(sched, worker, shift_type):
    if shift_type == "midshift":
        for shift in worker.request.midshift:
            avail_midshift = sched.has(shift, "midshift")
            # If there is a midshift to assign
            if avail_midshift != None:
                avail_midshift.num_workers -= 1
                avail_midshift.workers.append(worker)
                worker.assigned_hours += 6.25
                worker.assigned_shifts.append(avail_midshift)
                return True
        return False

def make_schedule(main_sched, workers):
    # First work on the midshift scheduling
    #  - First assign midshifts to all workers that want one
    #  - Next assign midshifts to workers that have to get one
    num_midshift = 14
    workers_left = main_sched.num_workers
    for indiv in workers:
        if num_midshift == workers_left:
            break
        if indiv.request.mid_pref == True and num_midshift > 0:
            # If a worker wants a midshift, go through the midshift preferences
            if assign_shift(main_sched, indiv, "midshift"):
                num_midshift -= 1
                break

    if num_midshift > 0:
        offset = main_sched.num_workers - num_midshift
        for indiv in workers[offset:]:
            if assign_shift(main_sched, indiv, "midshift") == False:
                err.write("ERROR: Midshift assignment failure\n")
                return 1

    if num_midshift != 0:
        err.write("ERROR: Midshift assignment failure - not all midshifts assigned\n")
        return 1




def main():
    a = Shift(23.75, 6, 0, 2)
    b = Shift(2, 3, 0, 1)
    sched = Schedule(12, 19.5, None, None)
    print sched.has(a, "midshift")

if __name__ == "__main__":
    main()

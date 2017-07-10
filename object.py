#!/usr/bin/env python

err = open("error_object.txt", "w")

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
#  1. list of midshifts in preferred order
#  2. list of desk shifts separated into preferred, available, and secondary
#  3. list of extra shifts separated into preferred, available, and secondary
#  5. midshift (yes/no)
#  6. number of requested hours
# - Every Worker will have a Schedule Request
# - Items 1 through 3 will be represented as a list of shifts in that order
# - Priority will be represented by the order that of the requests in a list
class Request(object):

    def __init__(self, midshift, desk_preferred, desk_available, desk_secondary, extra_preferred, extra_available, extra_secondary, midshift_pref, num_hours):
        self.shifts = []
        self.shifts.append(midshift)
        self.shifts.append(desk_preferred)
        self.shifts.append(desk_available)
        self.shifts.append(desk_secondary)
        self.shifts.append(extra_preferred)
        self.shifts.append(extra_available)
        self.shifts.append(extra_secondary)
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

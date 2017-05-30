#!/usr/bin/env python

# Shifts will have start times, end times, the day of the shift, and the amount of
#   workers that are needed
# Shifts will be used for both the main schedule and the schedule requests
class Shift(object):
    # 0 will represent Sunday, 1 = Monday, ... 6 = Saturday
    # Military time will be used to remain clear of confusion
    # Number of workers for shifts in schedule requests will always be 1

    def __init__(self, start, end, day, workers):
        self.start_time = start
        self.end_time = end
        self.weekday = day
        self.num_workers = workers


# We will have one main schedule representing the schedule we need to fill
class Schedule(object):
    # The schedule will contain minimum hours, maximum hours, list of midshifts,
    #   list of desk shifts, and a list of extra shifts.
    # The midshift will be stay the same, desk shifts will be able to be modified to
    #   change number of people working shifts (single staff or not)
    # The extra shifts can be modified as they will change every week.

    # Create the list of Shifts representing midshifts
    midshifts = [Shift(23.75, 6.0, i) for i in range(7)]


    # Initialize a new Schedule. We want to be able to change desk shifts (single staff
    #   shifts) and extra shifts
    def __init__(self, min_hours, max_hours, desk_shifts, extra_shifts):
        self.min_hours = min_hours
        self.max_hours = max_hours
        self.desk_shifts = desk_shifts
        self.extra_shifts = extra_shifts


# Every Worker will have a Schedule Request
# Requests will contain:
#  - hours that the worker will not be able to work
#  - list of midshift preferences
#  - list of preferred shifts
#  - list of available shifts
#  - list of secondary choice shifts
#  - name of the worker
#  - midshift (yes/no)
#  - number of requested hours
class Request(object):

    def __init__(self, name, unavailable, midshift, preferred, available, secondary, )


def main():


if __name__ == "__main__":
    main()

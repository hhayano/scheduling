#!/usr/bin/env python

import xlrd # For parsing excel sheets
import os
import object
import action
import test

err = open("error_scheduling.txt", "w")

def main():
    test.run_tests()

if __name__ == "__main__":
    main()

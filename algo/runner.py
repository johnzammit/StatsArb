# https://stackoverflow.com/questions/52722864/python-periodic-timer-interrupt
# https://en.wikipedia.org/wiki/Clock_drift


# idea 1:
# - create a timer thread
# - make it interrupt and run the loop every however many seconds
# - somehow need to ensure that we are not interrupting program if it is executing order
# - ensure program runs fast enough?, overwise it may never execute

# idea 2:
# - create a loop that keeps updating itself and executes when possible
# - set a minimum delay between each loop iteration, such that if we finish updating/executing early
#   then we will still not update/execute until we have reached that minimum delay


# probably go with idea 2
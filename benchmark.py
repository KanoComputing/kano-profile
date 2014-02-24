import kanoprofile as kp

app_name = 'test'

state = kp.load_app_state(app_name)

state['val1'] = 1
state['val2'] = 100


def f():
    global state
    state['val1'] += 1
    state['val2'] += 2

    kp.calculate_xp()


import timeit

number = 1000

time_all = timeit.timeit("f()", "from __main__ import f", number=number)
time_one = time_all / float(number)
times_per_second = 1 / time_one

print "millisecond for one: \t{0:.2f}".format(time_one * 1000)
print "times per second: \t{}".format(int(times_per_second))



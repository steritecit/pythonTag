import time

LOGGING = True


def log(func, sleepTime=0):
    def wrapper(*args, **kwargs):
        if LOGGING:
            print('\nFUNCTION: ', func.__name__)
            print('---------------')
            for arg in args:
                print(' -- Argument:', arg, ' TYPE:', type(arg))
            for key, val in kwargs.items():
                print(' -- KW Argument:', key, val, ' TYPE:', type(val))
            value = func(*args, **kwargs)
            print('   ------  Return Value: ',
                  value, ' TYPE:', type(value))
            time.sleep(sleepTime)
            return value
    return wrapper

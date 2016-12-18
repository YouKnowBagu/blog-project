from functools import wraps
arg1 = 'apple'
arg2 = 'banana'
arg3 = 'orange'
arg4 = 'pear'

superlist = [[arg1], [arg1, arg2],[arg1, arg2, arg3],[arg1, arg2, arg3, arg4]]

arglist = []


listortup = (1, 2, 3, 4, 5, 6)

def bar(function):
    @wraps(function)
    def foo(*args):
        newnum = 14
        twonum = 28
        threenum = 36
        global arglist
        arglist.append(newnum)
        arglist.append(twonum)
        arglist.append(threenum)
        nm = (len(args) - 1)
        helper = superlist[nm]
        i = 0
        while i <= nm:
            helper[i] = arglist[i]
            i += 1
        print helper
        return function(*helper)
    return foo

@bar
def returner(a, b, c):
    print a, b, c

returner(arg1, arg2, arg3)
print arglist
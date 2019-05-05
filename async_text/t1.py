from asyio import asyio
import time
# asyncio.wait()
def a():
    print('a is start')
    yield None
    yield 2
    yield 3

def compute(x, y):
    print("Compute %s + %s ..." % (x, y))
    # yield from a()
    yield from asyio.sleep(y)
    # yield 1
    return x + y

def print_sum(x, y):
    # arg = yield 3
    # print(f"arg {arg}")
    result = yield from compute(x, y)
    # yield from compute(2, 6)
    print("%s + %s = %s" % (x, y, result))


def inner():
    yield None
    yield None
    return 'aaa'


def tes_for_none():
    print("begin none")
    yield from inner()
    print("time eimt", time.time())
    print("aaaaaaaaaaaaa")


ts = [print_sum(1, 2), print_sum(1,4)]

futures = asyio.wait(ts)

print('time start', time.time())
loop = asyio.get_event_loop()
loop.run_until_complete(futures)

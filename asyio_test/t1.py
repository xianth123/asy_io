import asyio
import time


def compute(x, y):
    print("Compute %s + %s ..." % (x, y))
    yield from asyio.sleep(1)
    return x + y


@asyio.schedule_task(3)
def print_sum(x, y):
    print(time.time())
    result = yield from compute(x, y)
    print("%s + %s = %s" % (x, y, result))


loop = asyio.get_event_loop()
loop.run_not_complete(print_sum(1, 9))

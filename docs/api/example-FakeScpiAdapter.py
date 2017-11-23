from pymeasure.adapters import FakeScpiAdapter

a = FakeScpiAdapter(default_value=111, MEAS=33)
assert a.read() == ""
a.write("ABCD?")
assert a.read() == "111\n"  # default value
a.write("EFGH 4")
assert a.ask("EFGH?") == "4\n"
assert a.ask("MEAS?") == "33\n"

def handler(self, args=tuple(), query=False):
    if query:
        if args:
            return str(sum(args))
        else:
            return '0'

a.set_handler("SUM", handler)
assert a.ask("SUM? 1,2,3,4") == "10"

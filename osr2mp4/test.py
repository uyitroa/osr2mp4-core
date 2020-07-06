from autologging import logged, traced, TRACE
import logging

logging.basicConfig(
level=TRACE, stream=open("test.log", "w"),
format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")


@logged(logging.getLogger("my_function"))
@traced
def my_function(asdf):
    a = "1"
    asdf += "asdf"
    return asdf

my_function("123")

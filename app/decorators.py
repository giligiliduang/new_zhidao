
import blinker
def use_signal(signal):
    assert isinstance(signal, blinker.NamedSignal)

    def decorator(func):
        signal.connect(func)
        return func
    return decorator


def call(func, *args):
    def call_func(*call_args, **call_kwargs):
        func(*args, *call_args, **call_kwargs)
    return call_func


def ecall(func, *args):
    def call_func(*_, **__):
        func(*args)
    return call_func


def xapply (func, *args, **xargs):
  if type(args[-1])==list:
    args = args[0:-1] + tuple(args[-1])
  return apply(func, *args, **xargs)
  
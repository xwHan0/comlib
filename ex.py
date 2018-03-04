
doc = help

def xapply (func, *args, **xargs):
  """Execute 'fun' with parameter list args and xargs.
  
  args: A tuple reprents the parameter for 'func'.
        The last element of args can be a list represented remain parameter list.
  xargs: Named map represents a named parameter
  return: 'func' return value
  """
  if type(args[-1])==list:
    args = args[0:-1] + tuple(args[-1])
  return apply(func, *args, **xargs)
  
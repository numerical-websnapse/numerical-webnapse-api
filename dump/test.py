from latex2sympy2 import latex2sympy, latex2latex
from sympy import symbols, Function

tex = r"x_{1,1}+x_{2,1}"
expr = latex2sympy(tex)
print(expr)
print(expr.evalf(subs={"x_{1,1}":6, "x_{2,1}":5,"x_{3,1}":1}))
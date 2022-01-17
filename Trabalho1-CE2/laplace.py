import sympy

s = sympy.Symbol('s')

Gn = sympy.Matrix([[1/s,      0,       0,     0,     1],
                   [0,       1,       0,     1,     0],
                   [0,       0,      2*s,   -6,    -1],
                   [0,      -1,       1,     0,     0],
                   [-1,       5,       1,     0,     0]])

In = sympy.Matrix([[-12/s],
                   [10/s],
                   [10],
                   [0],
                   [0]])

print(f'Gn:\n{Gn}\n')
print(f'In:\n{In}\n')

e = Gn.inv()*In

for count in range(len(e)):
    print(f'e{count+1}: {e[count]}')
print()

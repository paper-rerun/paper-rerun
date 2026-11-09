import math
m = [0.02196, 3.034]
c = [[4.0311226e-07, 7.30390042e-05], [7.30390042e-05, 0.0452831584]]
nnu = 3.044
mu = m[0] + c[0][1] / c[1][1] * (nnu - m[1])
sd = math.sqrt(c[0][0] - c[0][1] ** 2 / c[1][1])
print("conditional omega_b", round(mu, 7), round(sd, 7))
print("marginal omega_b", m[0], round(math.sqrt(c[0][0]), 7))
print("chi2 floor", round((nnu - m[1]) ** 2 / c[1][1], 5))

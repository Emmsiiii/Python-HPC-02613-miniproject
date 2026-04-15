import numpy as np
import matplotlib.pyplot as plt

# STATIC
t1 = 25*60+22

num_proc = [1, 2, 5, 10, 15, 20, 25, 30]
speed_up_stat = [t1/t1 ,t1/(17*60 + 4),t1/(7*60+51), t1/(8*60+42), t1/(8*60+38), t1/(7*60+26), t1/(7*60+3), t1/(7*60+7) ]

# theoretical speed up
F = 0.75
p = np.linspace(0,30,100)
Sp = t1/((1-F)*t1+(F*t1)/p)

plt.plot(num_proc, speed_up_stat)
plt.plot(p,Sp, '--', label = "parallel fraction = 0.75")
plt.xlabel("number of processors")
plt.ylabel("Speed-up")
plt.title("Speed-up using static parallelization")
plt.legend()
plt.savefig("static.pdf", bbox_inches='tight')
plt.show()

# DYNAMIC
t1 = 22*60+10

num_proc = [1, 2, 5, 10, 15, 20, 25, 30]
speed_up_dy = [t1/t1 ,t1/(14*60 + 40),t1/(9*60+23), t1/(8*60+44), t1/(9*60+38), t1/(7*60+59), t1/(8*60+2), t1/(8*60+27) ]

# theoretical speed up
F = 0.65
p = np.linspace(0,30,100)
Sp = t1/((1-F)*t1+(F*t1)/p)

plt.plot(num_proc, speed_up_dy)
plt.plot(p,Sp, '--', label = "parallel fraction = 0.65")
plt.xlabel("number of processors")
plt.ylabel("Speed-up")
plt.title("Speed-up using dynamic parallelization (chunksize = 5)")
plt.legend()
plt.savefig("dynamic.pdf", bbox_inches='tight')
plt.show()


print(np.max(speed_up_stat))
print(speed_up_stat)

print(np.max(speed_up_dy))
print(speed_up_dy)
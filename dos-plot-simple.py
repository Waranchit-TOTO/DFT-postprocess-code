import matplotlib.pyplot as plt
import numpy as np

file = 'siesta.TBT.AVDOS'
data = np.loadtxt(file) #skip 3 rows
energy = data[3:,0]
dos = data[3:,1]

print(energy)

plt.plot(energy, dos)
plt.xlabel('Energy (eV)')
plt.ylabel('Density of States (states/eV)')
plt.title('Density of States from NEGF Calculation')
plt.grid()
plt.show()

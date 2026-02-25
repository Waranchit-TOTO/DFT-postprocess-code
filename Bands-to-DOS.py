# THIS EXAMPLE SUM THE DOS FROM BANDS OBTAINED FROM SIESTA. THE FIRST SECTION IS READING BANDS INFORMATION (FERMI, K RANGE, E RANGE)
# THEN DEAL WITH THE HEAD AND THE END OF FILE.

import numpy as np
import matplotlib.pyplot as plt

filename = "siesta.bands"
nb = 1044  # eigenvalues per k-point                                                ## CHECK YOUR OWN DATA ##

# Initialize lists to store k-points and eigenvalues
kpoints, eigvals = [], []
# Temporary variables to accumulate data for current k-point
current_k = None
current_eigs = []


# Open and read the Siesta bands file
with open(filename, "r") as f:
    for i, line in enumerate(f):
        if i == 0:
            # First line contains Fermi level information
            fermi_level = float(line.split()[0])  # Extract Fermi level value
        if i == 1:
            # Second line contains k-point range information
            k_start, k_end = map(float, line.split()[:2])  # Extract k-point range
        if i == 2:
            # Third line contains energy range information
            e_min, e_max = map(float, line.split()[:2])  # Extract energy range

        if i < 4:
            continue  #skip
        
        # Split line into individual values
        parts = line.strip().split()
        # Skip empty lines
        if not parts:
            continue #skip
        
        try:
            # Convert all string values to floats
            values = [float(x) for x in parts]
            # Count leading spaces to detect k-point vs continuation lines
            # K-point lines have ~2 spaces, continuation lines have ~14+ spaces
            indent = len(line) - len(line.lstrip())
            is_kpoint_line = indent < 5
            
            # When we reach a new k-point AND have accumulated 1044 eigenvalues,
            # save the previous k-point block to arrays
            if is_kpoint_line and current_eigs and len(current_eigs) >= nb:
                kpoints.append(current_k)
                eigvals.append(current_eigs[:nb])
                current_eigs = []  # Reset for next k-point
            
            # If this is a k-point line, extract k-point value (first number)
            # and start collecting eigenvalues (remaining numbers)
            if is_kpoint_line:
                current_k = values[0]  # First value is k-point coordinate
                current_eigs.extend(values[1:])  # Rest are eigenvalues
            else:
                # If continuation line, just add all values as eigenvalues
                current_eigs.extend(values)
        except ValueError:
            # Skip lines that can't be converted to floats
            pass

# After loop ends, save the final k-point block
if current_eigs and len(current_eigs) >= nb:
    kpoints.append(current_k)
    eigvals.append(current_eigs[:nb])

# Convert Python lists to NumPy arrays for efficient numerical operations
eigvals = np.array(eigvals)
kpoints = np.array(kpoints)

# Display results
print(f"Loaded {len(kpoints)} k-points, {len(eigvals[0])} eigenvalues each")
print(f"Shape: {eigvals.shape}")
print('K-points check:', kpoints[1:6], '... and last:', kpoints[-6:])  # Print first 5 k-points for verification
print('Eigenvalues check:', eigvals[0, :6], '... and last:', eigvals[-1, -6:])  

print(f"Fermi level: {fermi_level} eV")
print(f"K-point range: {k_start} to {k_end}")
print(f"Energy range: {e_min} to {e_max} eV")


#============================= End of data loading =============================

Q = input("Plot bands? (yes/no): ")  # Wait for user input before plotting
if Q.lower() != "yes":
    print("Exiting without plotting.")
    #exit()

if Q.lower() == "yes":
    plt.figure(figsize=(8, 6))
    for i in range(eigvals.shape[1]):
        plt.scatter(kpoints, eigvals[:, i]-fermi_level, color='blue', linewidth=0.5)  # Plot each band with thin blue lines
    plt.xlabel('K-point')
    plt.ylabel('Energy (eV)')
    plt.title('Band Structure')
    plt.grid(True)
    plt.tight_layout()
    plt.ylim(-2,2)
    plt.show()  

#============================= End of plotting =============================

#===================== Gaussian function for broadening ====================
def gauss(x, mu, sigma):
    return 1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2))
#===================== End of Gaussian function ====================

#=================== Testing the guassian function ===================
Q = input("Test Gaussian function? (yes/no): ")  # Wait for user input before testing
if Q.lower() != "yes":
    print("Skipping Gaussian function test.")
    #exit()

if Q.lower() == "yes":
    x = np.linspace(-5, 5, 1000) 
    sigma = float(input("sigma = ")) #np.sqrt(0.2)

    plt.figure(figsize=(8, 6))
    plt.plot(x, gauss(x, 0, sigma), label=f'Gaussian with σ={sigma}', color='red')
    plt.xlabel('Energy (eV)')
    plt.ylabel('Density of States')
    plt.title('Gaussian Function Test')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

#=================== End of Gaussian function test ===================

#=================== DOS calculation with Gaussian broadening ===================

sigma = float(input("sigma = "))  # Broadening parameter
energy_range = np.linspace(e_min, e_max, 10000)  # Energy range for DOS calculation

dos = np.zeros_like(energy_range) # making array of zeros matching to energy range grids
#print(dos)

print("calculating DOS with Gaussian broadening...")

for i in range(eigvals.shape[0]):
    for j in range(eigvals.shape[1]):
        #dos = np.append(dos, gauss(energy_range, eigvals[i, j], sigma))  # Add Gaussian contributions from each eigenvalue
        dos += gauss(energy_range, eigvals[i, j], sigma)  # Add Gaussian contributions from each eigenvalue

dos /= eigvals.shape[0]

plt.figure(figsize=(8, 6))
plt.plot(energy_range - fermi_level, dos, label='DOS with Gaussian broadening', color='green')
plt.xlabel('Energy (eV)')
plt.ylabel('Density of States')
plt.title('Density of States')

Q = input("input energy range for zooming in (e.g. -1,1): ")
Q = Q.split(',')
Q = [float(x.strip()) for x in Q]
plt.xlim(Q[0], Q[1])

Q = input("input energy range for y-axis (recommend 0,100): ")
Q = Q.split(',')
Q = [float(x.strip()) for x in Q]
plt.ylim(Q[0], Q[1])

plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
#print(dos)
#=================== End of DOS calculation ===================

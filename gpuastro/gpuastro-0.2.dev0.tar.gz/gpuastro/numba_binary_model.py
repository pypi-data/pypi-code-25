'''
/*∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗
∗ ∗
∗ This program is free software; you can redistribute it and/or modify ∗
∗ it under the terms of the GNU General Public License as published by ∗
∗ the Free Software Foundation; either version 2 of the License, or ∗
∗ (at your option) any later version. ∗
∗ ∗                                                                     * *
* *                   Email : s.gill@keele.ac.uk                        * *
* *                   github : samgill844                               * *
∗ ∗                                                                     * *
∗ Acknowledgments:                                                      * *
* The equations in the section "Keplerian equations" is ported from     * *
* the lightcurve model "ellc" (Maxted 2016), as is the function in      * *
* the "Radial velocity equations" section.                      
∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗*/
'''

'''
/*∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗
                          User choices
∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗*/
'''
# First check if any GPUs are knockign about...
try:
	from numba import cuda
	GPU_capability = cuda.detect()
	#GPU_capability = 0
	if GPU_capability: 
		print('\tGPU acceleration enabled')
		PURE_PYTHON = False
		NUMBA_CPU = False
		NUMBA_GPU = True
		CUDA_FLAG=1

except:
	try:
		from numba import jit
		print('\tCPU acceleration only')
		PURE_PYTHON = False
		NUMBA_CPU = True
		NUMBA_GPU = False
		CUDA_FLAG=0
	except:
		print('\tPure python  only')
		PURE_PYTHON = True
		NUMBA_CPU = False
		NUMBA_GPU = False
		CUDA_FLAG=0

		



'''
/*∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗
                          Import statements
∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗*/
'''
# Core required imports
import numpy as np
import matplotlib.pyplot as plt
import math


'''
/*∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗
                          Keplerian equations
∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗*/
'''
def eanom(m, e):
	m = m % (2*math.pi)
	if m > math.pi : m = 2*math.pi - m; flip=1
	else : flip=0

	it = 0
	test = 99
	e1 = math.fmod(m,2*math.pi) + e*math.sin(m) + e*e*math.sin(2.0*m)/2.0

	e0 = 0
	while test > 1e-8:
		e0 = e1
		e1 = e0 + (m-(e0 - e*math.sin(e0)))/(1.0 - e*math.cos(e0))
		test = math.fabs(e1 - e0)
		it+=1
		
		if it > 10000: 
			raise ValueError('Did not converge')

	e1 = math.fmod(e1, 2*math.pi) 

	#if e1 < 2*math.pi : e1 = e1 + 2*math.pi
	if flip==1 : e1 = 2*math.pi - e1
	return e1

def trueanom(m,e):
	ee = eanom(m,e)
	return 2.0*math.atan(math.sqrt((1.0 + e)/(1.0 - e))*math.tan(ee/2.0))



def delta_func(theta, efac, sin2i, omega, ecc):
	return efac*math.sqrt(1.0 - sin2i*math.sin(theta+omega)**2)/(1.0+ecc*math.cos(theta))

def t_ecl_to_peri(t_ecl, ecc, omega, incl, p_sid):
	efac = 1 - ecc**2
	sin2i = math.sin(incl)**2
	theta_0 = math.pi/2 - omega #  True anomaly at superior conjunction


	if (incl != (math.pi/2)):
		theta_old = theta_0
		theta_trial = theta_0

		diff_old = delta_func(theta_old, efac, sin2i, omega, ecc)
		diff_trial = 1000  

		step = 0.01
		while diff_trial < 1e-5:
			theta_trial = theta_old + step
			diff_trial = delta_func(theta_trial, efac, sin2i, omega, ecc)
			if diff_trial < diff_old:
				# Better step
				theta_old = theta_trial
				diff_old = diff_trial
			else:
				# Worse step, change direction and size
				step = -0.5*step		
		theta = theta_old
	else :  
		theta = theta_0

	if theta == math.pi : ee = math.pi
	else :  ee = 2.0 * math.atan(math.sqrt((1.0-ecc)/(1.0+ecc)) * math.tan(theta/2.0))

	eta = ee - ecc*math.sin(ee)	
	
	delta_t = eta*p_sid/(2*math.pi)
	return t_ecl  - delta_t



'''
/*∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗
                        Radiall velocity equations
∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗*/
'''

def rv_jit(t, RV1, RV2,  t_zero, period, K1, K2, fs, fc, V0, dV0, incl, CUDA_FLAG, n_elements):
	# Calculate the mean anomaly
	
	if CUDA_FLAG==0:
		# Preliminary conversions
		incl = math.pi*incl/180
		e = fs**2 + fc**2
		if fc != 0 : w = math.atan2(fs,fc)
		else : w = 0

		for i in range(t.shape[0]):
			mean_anomaly = 2*math.pi* math.fmod((t[i] - t_ecl_to_peri(t_zero, e, w, incl, period))/period, 1.0)

			if e==0:
				RV1[i] = K1*math.cos(mean_anomaly + w)              + V0  + dV0*(t[i] - t_zero)
				RV2[i] = K2*math.cos(mean_anomaly + w + math.pi)    + V0  + dV0*(t[i] - t_zero)
			else:
				RV1[i] = K1*( e*math.cos(w) + math.cos(trueanom(mean_anomaly, e) + w ))              + V0  + dV0*(t[i] - t_zero)
				RV2[i] = K2*( e*math.cos(w) + math.cos(trueanom(mean_anomaly, e) + w + math.pi ))    + V0  + dV0*(t[i] - t_zero)

	
	if CUDA_FLAG==1:
		# Preliminary conversions
		incl = math.pi*incl/180
		e = fs**2 + fc**2
		if fc != 0 : w = math.atan2(fs,fc)
		else : w = 0

		# Get thread ID
		# This is a tricky call since cuda.grid() is not defined when using the CPU jit, 
		# and is why we hacked cuda.jit to return
		i = cuda.grid(1)
		if i < n_elements:
			# Get the mean anomaly
			mean_anomaly = 2*math.pi*math.fmod((t[i] - t_ecl_to_peri(t_zero, e, w, incl, period))/period, 1.0)

			# Calculate RV1 and RV2
			if e==0:
				RV1[i] = K1*math.cos(mean_anomaly + w)              + V0  + dV0*(t[i] - t_zero)
				RV2[i] = K2*math.cos(mean_anomaly + w + math.pi)    + V0  + dV0*(t[i] - t_zero)
			else:
				RV1[i] = K1*( e*math.cos(w) + math.cos(trueanom(mean_anomaly, e) + w ))            + V0  + dV0*(t[i] - t_zero)
				RV2[i] = K2*( e*math.cos(w) + math.cos(trueanom(mean_anomaly, e) + w + math.pi ))    + V0  + dV0*(t[i] - t_zero)
	


def rv(t, t_zero=0.0, period=1.0, K1=10, K2=10, fs=0, fc=0, V0=10, dV0=0, incl=90):
	# Convert time to float32
	t = np.array(t).astype(np.float32)

	# Initialise the return RV arrays
	RV1, RV2 = np.zeros(t.shape).astype(np.float32), np.zeros(t.shape).astype(np.float32)

	# type conversion
	t_zero = np.float32(t_zero)
	period = np.float32(period)
	K1 = np.float32(K1)
	K2 = np.float32(K2)
	fs = np.float32(fs)
	fc = np.float32(fc)
	V0 = np.float32(V0)
	dV0 = np.float32(dV0)
	incl = np.float32(incl)
	size = t.shape[0]

	# First test if the GPU is going to be used
	if CUDA_FLAG and not PURE_PYTHON:
		# Define the block size
		block_size = 512
		grid_size = int(np.ceil(size/block_size))
		blockdim = (block_size, 1, 1)
		griddim = (grid_size, 1)   

		# Make the call to the GPU
		rv_jit[griddim, blockdim](t, RV1, RV2,  t_zero, period, K1, K2, fs, fc, V0, dV0, incl, CUDA_FLAG, size)

	# The check if the CPU jit or pure python call is needed
	elif not CUDA_FLAG or PURE_PYTHON:
		rv_jit(t, RV1, RV2,  t_zero, period, K1, K2, fs, fc, V0, dV0, incl, CUDA_FLAG, size)

	return RV1, RV2



'''
/*∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗
                          Lightcurve equations
∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗*/
'''

def a_from_Kepler(period, M1, Q):
	# Calculate the orbital seperation through keplers laws
	#
	# Uses:
	#	period - the period of the system
	#	M1 	   - the mass of the system (solar mass)
	#	Q      - the mass ratio of the primary and secondary
	#

	# Constants
	M_Sun = 1.989e30
	G = 6.67408e-11
	a = 149597870700.0

	# Conversion
	period = period*24*60*60 # [day] -> [s]
	M1 = M1 * M_Sun
	return ( (period**2 * G*M1*(1+Q)) / (4*math.pi**2) )**(1/3) / a


def scaled_orbital_seperation(e, incl, true_anomaly, argument_of_periastron):
	# Returns the scaled orbital seperation in units of "a"
	#
	# Uses : 
	#	e 		- eccentricity
	#	incl 	- inclination (RADIANS)
	#	m 		- true_anomaly
	#	w 		- argument of periastron
	#
	return (1-e**2) * math.sqrt( 1 - math.sin(incl)**2 * math.sin(true_anomaly + argument_of_periastron)**2) / (1 + e*math.sin(true_anomaly));


def get_I_from_limb_darkening(ld_law,  ldc, mu_i):
	'''
	Calculte limb-darkening for a variety of laws e.t.c.

	[0] linear (Schwarzschild (1906, Nachrichten von der Königlichen Gesellschaft der Wissenschaften zu Göttingen. Mathematisch-Physikalische Klasse, p. 43)
	[1] Quadratic Kopal (1950, Harvard Col. Obs. Circ., 454, 1)
	[2] Square-root (Díaz-Cordovés & Giménez, 1992, A&A, 259, 227) 
	[3] Logarithmic (Klinglesmith & Sobieski, 1970, AJ, 75, 175)
	[4] Exponential LD law (Claret & Hauschildt, 2003, A&A, 412, 241)
	[5] Sing three-parameter law (Sing et al., 2009, A&A, 505, 891)
	[6] Claret four-parameter law (Claret, 2000, A&A, 363, 1081)
	[7] Power-2 law (Maxted 2018 in prep)
	'''

	if ld_law == 0 : return 1 - ldc[0]*(1 - mu_i)
	if ld_law == 1: return 1 - ldc[0]*(1 - mu_i) - ldc[1] * (1 - mu_i)**2         
	if ld_law == 2: return 1 -  ldc[0]*(1 - mu_i) - ldc[1]*(1 - mu_i**2 ) 
	'''
	if ld_law == 3: return 1 -  ldc[0]*(1 - mu_i) - ldc[1]*mu_i*math.log(mu_i); 
	if ld_law == 4: return 1 -  ldc[0]*(1 - mu_i) - ldc[1]/(1-math.exp(mu_i));  
	if ld_law == 5: return 1 -  ldc[0]*(1 - mu_i) - ldc[1]*(1 - mu_i**1.5) - ldc[2]*(1 - mu_i**2);
	if ld_law == 6: return 1 - ldc[0]*(1 - mu_i**0.5) -  ldc[1]*(1 - mu_i) - ldc[2]*(1 - mu_i**1.5)  - ldc[3]*(1 - mu_i**2);
	if ld_law == 7: return 1 - ldc[0]*(1 - mu_i**ldc[1])
	
	'''

def lc_jit(t, Flux, t_zero, period, radius_1, k , fs, fc, ld_law, ldc, incl, a, CUDA_FLAG, n_elements):
	# Calculate the mean anomaly
	if CUDA_FLAG==0:

		x = 2

		# Preliminary conversions
		incl = math.pi*incl/180
		e = fs**2 + fc**2
		if fc != 0 : w = math.atan2(fs,fc)
		else : w = 0
		radius_2 = k*radius_1

		# Step 1
		# divides the sky-projected stellar disk into a user-defined
		# number of annuli, n, with uniform radial separation,
		# dr n = 1 ;		
		n_annuli = 1000
		dr = 1.0/n_annuli

		for i in range(n_elements):
			# First calculate the mean and true anomaly
			mean_anomaly = 2*math.pi* math.fmod((t[i] - t_ecl_to_peri(t_zero, e, w, incl, period))/period, 1.0)
			eccentric_anomaly = eanom(mean_anomaly, e)
			true_anomaly = trueanom(mean_anomaly, e)

			# Calculate the orbital seperation, if needed
			if a==0 : d = a_from_Kepler(period, 1, 0.2)*scaled_orbital_seperation(e, incl, true_anomaly, w)
			else : d = a*scaled_orbital_seperation(e, incl, true_anomaly, w)
			#au = 149597870700.0
			#R_sun = 695700000.0
			#d_radius = d*au / constants.R_sun.value
			d_radius = d*149597870700.0 / 695700000.0


			F_tot = 0.0
			F_occ = 0.0
			F_i = 0.0

			# Step 3.5
			# Calculate the star 1
			f = 2.*math.atan(math.sqrt((1.+e)/(1.-e))*math.tan(eccentric_anomaly/2.))
			f = math.sin(f + w)*math.sin(incl)

			if (f>0) and (d_radius< radius_1 + radius_2):
				for j in range(n_annuli):
					# Step 2
					#  evaluates the intensity at the central radius of each annulus,
					# I (ri), where ri = + ( ) 0.5 i n for i n = - 0 ... 1, interpolating
					# in μ from the input stellar-intensity profile (and ri = -1 mi2 );
					r_i = radius_1*(0.5 + j)/n_annuli
					mu_i = math.sqrt(1.0 - r_i*r_i)
					
					I_r_i = get_I_from_limb_darkening(ld_law,  ldc, mu_i) # 
					
					# Step 3
					# evaluates the flux from each annulus, F I r r dr ii i = ´ ( ) 2p ,
					# and hence the total stellar flux, * = å = - F i F
					F_i = I_r_i*2*math.pi*r_i*d_radius
					F_tot = F_tot + F_i


					# Step 4
					# Calcualte the fraction occulted
					# First check if disk 2 is entirely covered by disk 1 (or occulted)
					if (r_i <= (radius_2-d_radius )) and (f>0):	F_occ= F_occ + F_i; continue
					elif (r_i <= (d_radius-radius_2)) or (r_i >= (d_radius+radius_2))  and (f>0): continue
					elif (abs(d_radius - radius_2) < r_i) and (r_i < (d_radius + radius_2))  and (f>0): F_occ += F_i*math.acos((r_i**2 + d_radius**2 - radius_2**2)/(2*d_radius*r_i) )/math.pi ; continue
					
				# Put in the flux
				Flux[i] =   1 - F_occ/F_tot
					


	
	if CUDA_FLAG==1:

		# Get thread ID
		# This is a tricky call since cuda.grid() is not defined when using the CPU jit, 
		# and is why we hacked cuda.jit to return
		i = cuda.grid(1)

		# Preliminary conversions
		incl = math.pi*incl/180
		e = fs**2 + fc**2
		if fc != 0 : w = math.atan2(fs,fc)
		else : w = 0
		radius_2 = k*radius_1

		# Step 1
		# divides the sky-projected stellar disk into a user-defined
		# number of annuli, n, with uniform radial separation,
		# dr n = 1 ;		
		n_annuli = 1000
		dr = 1.0/n_annuli

		# First calculate the mean and true anomaly
		mean_anomaly = 2*math.pi* math.fmod((t[i] - t_ecl_to_peri(t_zero, e, w, incl, period))/period, 1.0)
		eccentric_anomaly = eanom(mean_anomaly, e)
		true_anomaly = trueanom(mean_anomaly, e)

		# Calculate the orbital seperation, if needed
		if a==0 : d = a_from_Kepler(period, 1, 0.2)*scaled_orbital_seperation(e, incl, true_anomaly, w)
		else : d = a*scaled_orbital_seperation(e, incl, true_anomaly, w)
		#au = 149597870700.0
		#R_sun = 695700000.0
		#d_radius = d*au / constants.R_sun.value
		d_radius = d*149597870700.0 / 695700000.0


		F_tot = 0.0
		F_occ = 0.0
		F_i = 0.0

		# Step 3.5
		# Calculate the star 1
		f = 2.*math.atan(math.sqrt((1.+e)/(1.-e))*math.tan(eccentric_anomaly/2.))
		f = math.sin(f + w)*math.sin(incl)
		#Flux[i] = f
	

		if (f>0) and (d_radius< radius_1 + radius_2):
			for j in range(n_annuli):
				# Step 2
				#  evaluates the intensity at the central radius of each annulus,
				# I (ri), where ri = + ( ) 0.5 i n for i n = - 0 ... 1, interpolating
				# in μ from the input stellar-intensity profile (and ri = -1 mi2 );
				r_i = radius_1*(0.5 + j)/n_annuli
				mu_i = math.sqrt(1.0 - r_i*r_i)
				
				I_r_i = get_I_from_limb_darkening(ld_law,  ldc, mu_i)
				
				# Step 3
				# evaluates the flux from each annulus, F I r r dr ii i = ´ ( ) 2p ,
				# and hence the total stellar flux, * = å = - F i F
				F_i = I_r_i*2*math.pi*r_i*d_radius
				F_tot = F_tot + F_i


				# Step 4
				# Calcualte the fraction occulted
				# First check if disk 2 is entirely covered by disk 1 (or occulted)
				if (r_i <= (radius_2-d_radius )) and (f>0):	F_occ= F_occ + F_i; continue
				elif (r_i <= (d_radius-radius_2)) or (r_i >= (d_radius+radius_2))  and (f>0): continue
				elif (abs(d_radius - radius_2) < r_i) and (r_i < (d_radius + radius_2))  and (f>0): F_occ += F_i*math.acos((r_i**2 + d_radius**2 - radius_2**2)/(2*d_radius*r_i) )/math.pi ; continue
				
			# Put in the flux
			Flux[i] =   1 - F_occ/F_tot
	
		

def lc(t, t_zero=0.0, period=1.0, radius_1 = 0.2, k = 0.2, fs=0, fc=0, incl=90, ld_law=0, ldc = [0.6]):
	# Convert time to float32
	t = np.array(t).astype(np.float32)

	# Convert ldc
	ldc = np.array(ldc).astype(np.float32)

	# Initialise the return Flux array
	Flux = np.ones(t.shape).astype(np.float32)
	ld_law = np.int(ld_law)

	# type conversion
	t_zero = np.float32(t_zero)
	period = np.float32(period)
	fs = np.float32(fs)
	fc = np.float32(fc)
	incl = np.float32(incl)
	size = t.shape[0]

	# First test if the GPU is going to be used
	if CUDA_FLAG and not PURE_PYTHON:
		# Define the block size
		block_size = 512
		grid_size = int(np.ceil(size/block_size))
		blockdim = (block_size, 1, 1)
		griddim = (grid_size, 1)   

		# Make the call to the GPU
		lc_jit[griddim, blockdim](t, Flux, t_zero, period, radius_1, k, fs, fc, ld_law, ldc, incl,0, CUDA_FLAG, size)

	# The check if the CPU jit or pure python call is needed
	elif not CUDA_FLAG or PURE_PYTHON:
		lc_jit(t, Flux, t_zero, period, radius_1, k, fs, fc, ld_law, ldc, incl,0, CUDA_FLAG, size)

	return Flux


'''
/*∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗
                             Jit handeling 
∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗*/
'''
# Here we check the users input to make sure only one choice is made.
# After that we use the appropriate choice to proces the functions,
#
# Pure python:
#	~ Nothing changes the function - CUDA_FLAG set to zero.
#
# NUMBA_CPU:
#	~ The functions are 'jitted' with the numba wrappers for speed.
#	  The CUDA_FLAG is set to zero
#
# NUMBA_GPU:
#	~ The cuda drivers are imported and the functions are jitted accordingly.
#	  The CUDA_FLAG is set to 1, which means the function call is slightly different.
#	  The block and grid size is calculated based on the length of the array. 

# Global var initiased for ease later
cuda = 1

# First check to make sure only one choice is made
if PURE_PYTHON + NUMBA_CPU + NUMBA_GPU > 1:
	raise ValueError('Only one can be True: PURE_PYTHON, NUMBA_CPU, NUMBA_GPU')

if PURE_PYTHON:
	CUDA_FLAG=0
	print('\tPure python only')	

if NUMBA_CPU:
	from numba import jit, autojit
	CUDA_FLAG=0
	class x:
		@autojit
		def grid(self):
			return 1
	cuda = x()	

	# Keplerian jits
	eanom = jit(eanom)
	trueanom = jit(trueanom)
	delta_func = jit(delta_func)
	t_ecl_to_peri = jit(t_ecl_to_peri)

	# RV jits
	rv_jit = jit(rv_jit)

	# LC jit
	a_from_Kepler = jit(a_from_Kepler)
	scaled_orbital_seperation = jit(scaled_orbital_seperation)
	get_I_from_limb_darkening = jit(get_I_from_limb_darkening)
	lc_jit = jit(lc_jit)

	print('\tCPU JIT acceration enabled')

if NUMBA_GPU:
	from numba.cuda import jit
	from numba import cuda
	CUDA_FLAG=1

	# Keplerian device functions
	eanom = jit(eanom, device=True)
	trueanom = jit(trueanom, device=True)
	delta_func = jit(delta_func, device=True)
	t_ecl_to_peri = jit(t_ecl_to_peri, device=True)

	# Radial velocity glabal functions
	rv_jit = jit(rv_jit)

	# LC global functions
	a_from_Kepler = jit(a_from_Kepler, device=True)
	scaled_orbital_seperation = jit(scaled_orbital_seperation, device=True)
	get_I_from_limb_darkening = jit(get_I_from_limb_darkening, device=True)

	lc_jit = jit(lc_jit)
	print('\tGPU JIT acceration enabled')


'''
/*∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗
                             Test plot 
∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗∗*/
'''

def test():
	N = 2**10
	t = np.linspace(-0.06,0.06,N).astype(np.float32)

	plt.figure(1)
	plt.subplot(211)


	# LC test

	Flu = lc(t, radius_1=0.5, k=0.2, ld_law=0, ldc = [0.6])
	fig1 = plt.plot(t,-2.5*np.log10(Flu), label = 'lin')
	
	
	Flu = lc(t, radius_1=0.5, k=0.2, ld_law=1, ldc = (0.5,0.5))
	plt.plot(t,-2.5*np.log10(Flu), label = 'quad')
	
	Flu = lc(t, radius_1=0.5, k=0.2, ld_law=2, ldc = (0.5,0.5))
	plt.plot(t,-2.5*np.log10(Flu), label = 'sqrt')
	
	plt.legend()
	plt.xlabel('T - T_mid [d]')
	plt.ylabel('mag')

	plt.gca().invert_yaxis()


	# RV test

	plt.subplot(212)

	t = np.linspace(0,1,N).astype(np.float32)

	RV1, RV2 = rv(t, fc= 0.4, fs=0.4)
	fig2 = plt.plot(t, RV1, label='RV 1')
	plt.plot(t, RV2, label='RV 1')
	plt.legend()
	plt.xlabel('Phase')
	plt.ylabel('RV [km/s]')
	plt.show()

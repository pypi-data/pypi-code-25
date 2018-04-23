# TODO: buffer, peak find/label, averaging mode scans, save mismatch vs time data
# TODO: fix zero level offset in OMC DCPD

import cdsutils
import matplotlib.pyplot as plt
import numpy as np
from subprocess import check_output
from OMC_scan_funs_no_pandas_v2 import stage2, stage3

omc_channel_name = 'H1:OMC-DCPD_SUM_OUT_DQ'
pzt_channel_name = 'H1:OMC-PZT2_EXC'

def lets_go():
	fig1 = plt.figure()
	ax1 = fig1.add_subplot(411)
	ax2 = fig1.add_subplot(412)
	ax3 = fig1.add_subplot(413)
	ax4 = fig1.add_subplot(414)
	plt.show(block=False)

	ts = []
	mismatches = []
	while True:
		t_now = check_output(['tconvert', 'now'])
		# carefully chosen as pzt excitation period to avoid 
		# multiple omc vals at a single pzt val
		duration = 10 
		# grab one second before current time because the current
		# second might not have been uploaded by nds yet
		offset = 1
		t_start = int(t_now) - duration - offset
		omc_data_obj = cdsutils.getdata(omc_channel_name,duration,t_start)
		pzt_data_obj = cdsutils.getdata(pzt_channel_name,duration,t_start)
		if omc_data_obj is None or pzt_data_obj is None:
			print('empty data_obj returned')
			continue
		omc = omc_data_obj.data
		pzt = pzt_data_obj.data

		sort_ind = np.argsort(pzt)
		pzt_sort = pzt[sort_ind]
		omc_sort = omc[sort_ind]

		# data needs to be packaged this way for OMC_scan lib
		dc = {}
		dc['omc'] = omc_sort
		dc['pzt'] = pzt_sort

		#TODO: define better deltas
		delta_upper = np.max(dc['omc'])/1.3
		delta_lower = np.min(np.abs(dc['omc']))*3
		delta = 1e-4 # chosen for noise plotting

		dc2,p,fit0 = stage2(dc,delta_lower=delta_lower,delta_upper=delta_upper)
		#TODO: make stage3 return peak locs/labels (useful for visually tracking algo errors)
		mismatch = stage3(dc2,delta = delta,verbose=False)
		
		#TODO: write out these two in append mode to some file
		ts.append(t_now)
		mismatches.append(mismatch)

		xdata = np.linspace(t_start,t_start+10,len(omc))

		ax1.clear()
		ax2.clear()
		ax3.clear()
		ax4.clear()
		ax1.plot(xdata,pzt)
		ax2.plot(xdata,omc)
		ax3.plot(dc2['freq'],dc2['omc'])
		#TODO: plot peak locs here
		# ax3.plot(pzt_sort[peak_ind],omc_sort[peak_ind],'x',c='r',ms=6,mew=2)		
		ax4.plot(ts,mismatches)
		plt.pause(0.1) # it's like plt.draw() + sleep(0.1)
	return

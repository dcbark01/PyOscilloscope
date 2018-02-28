""" 
@author: Daniel C. Barker

For Rigol MSO4000 Oscilloscope programming guide, please see this link:
http://int.rigol.com/File/TechDoc/20160831/DS4000E_ProgrammingGuide_EN.pdf


"""


import numpy as np
import matplotlib.pyplot as plt
import sys
import visa
import re


class MyScope(object):

	def __init__(self, driver):
		""" Constructor Method. """
		self.driver = driver
		self.max_points = {'BYTE': 250000, 'WORD': 125000, 'ASCII': 15625}
		self.num_horiz_grids = 14   # Hard set according to the Rigol MSO4000 documentation
		
	""" ============== GENERIC/SETUP METHODS ===================== """
		
	def run(self):
		return self.driver.write(":RUN")
		
	def stop(self):
		return self.driver.write(":STOP")
	
	def clear(self):
		return self.driver.write(":CLEar")
		
	def autoscale(self):
		return self.driver.write(":AUToscale")
		
	def single_trigger(self):
		return self.driver.write(":SINGle")
		
	def close(self):
		return self.driver.close()
		
	def set_waveform_channel(self, channel):
		if channel == 1:
			ch_num = "CHANnel1"
		elif channel == 2:
			ch_num = "CHANnel2"
		elif channel == 3:
			ch_num = "CHANnel3"
		elif channel == 4:
			ch_num = "CHANnel4"
		else:
			print("Not a valid channel - RigolMSO4024 channels allow only 1-4")
			raise AssertionError
		command_str = ":WAVeform:SOURce " + ch_num
		return self.driver.write(command_str)
		
	def set_waveform_mode(self, mode):
		""" Set the waveform mode to """
		assert mode in ['NORM', 'NORMal', 'MAX', 'MAXimum', 'RAW']
		command_str = ":WAV:MODE " + mode
		return self.driver.write(command_str)
		
	def set_waveform_format(self, fmt):
		""" Sets waveform format to WORD, BYTE or ASCII. 
		Inputs:
			fmt		::	(str) Valid inputs are 'WORD', 'BYTE' or 'ASCII'
		Returns:
			None
		"""
		# Check to make sure the desired format is valid per Rigol documentation
		assert fmt in ['BYTE', 'WORD', 'ASCII']
		command_str = ":WAVeform:FORMat " + fmt
		return self.driver.write(command_str)
		
	def set_waveform_numpoints(self, points):
		""" Sets the number of points to store for the waveform. """
		return self.driver.write("WAVeform:POINts " + str(points))
		
	def set_waveform_start(self, pstart):
		""" Sets the point to START grabbing waveform data given integer input. """
		assert type(pstart) is int
		return self.driver.write(":WAV:STAR " + str(pstart))
		
	def set_waveform_end(self, pend):
		""" Sets the point to END grabbing waveform data given integer input. """
		assert type(pend) is int
		return self.driver.write(":WAV:STOP " + str(pend))
	
	
	""" ================== STATUS METHODS ===================== """
	def query_isfinished(self):
		""" Test to see if the current operation is done. 
		Inputs:
			None
		Returns:
			(bool) True if scope operation finished, False if not finished
		"""
		return np.int(self.driver.query("*OPC?"))
	
		
	""" ================== QUERYING METHODS ===================== """
	def query_memdepth(self):
		""" Get the memory depth storage value. 
		Inputs:
			None
		Returns:
			np.int (ex. memory_depth = MyScope.query_memdepth() >> 280000
		"""
		mem_depth = np.int(self.driver.query(":ACQuire:MDEPth?"))
		print("Current Memory Depth = " + str(mem_depth))
		return mem_depth
		
	def query_waveform_data(self):
		""" Get the stored waveform data. """
		return self.driver.query("WAV:DATA?")[10:]
		
	def query_sample_rate(self):
		""" Return the current sample rate setting for the scope. """
		ds = np.float(self.driver.query(":ACQuire:SRATe?"))
		print("Current Sample Rate = " + str(ds))
		return ds
		
	def query_horiz_timebase(self):
		""" Return the horizontal time base currently set for the scope. """
		tb = np.float(self.driver.query(":TIMebase:SCALe?"))
		print("Current Horizontal Time Base = " + str(tb) + " seconds")
		return tb
		
			
	""" ================== HIGH-LEVEL QUERY METHODS ============= """
	def query_ascii_data_singlebatch(self, channel, mode, fmt, pstart, pend):
		""" Wraps the lower level methods above to try to cleaningly get data. """
		self.stop()
		self.set_waveform_channel(channel)
		self.set_waveform_mode(mode)
		self.set_waveform_format(fmt)
		self.set_waveform_start(pstart)
		self.set_waveform_end(pend)
		rawdata = self.query_waveform_data()
		# convert to numpy array
		arr = np.array(re.split(",", rawdata))
		return arr
		
	
	""" ================== WAVEFORM SAVING METHODS ============= """
	def save_waveform_csv(self, usb_loc, file_name):
		""" Save the current waveform as a csv file. """
		# Check whether USB flash drive is inserted into front or back scope port
		if usb_loc is 'FRONT':
			fp = 'D:/'
		elif usb_loc is 'BACK':
			fp = 'E:/'
		else:
			print("USB flash drive must be inserted and usb_loc set to FRONT or BACK accordingly!")
			raise AssertionError
		full_path = fp + file_name
		print(full_path)
		self.driver.write(":SAVE:CSV:STARt " + full_path)
		
		
		
		

if __name__ == "__main__":	

	# Quick test script to see if we can connect to scope
	rm = visa.ResourceManager()
	# Get the USB device, e.g. 'USB0::0x1AB1::0x0588::DS1ED141904883'
	instruments = rm.list_resources()
	usb = list(filter(lambda x: 'USB' in x, instruments))
	if len(usb) != 1:
		print('Bad instrument list', instruments)
		sys.exit(-1)	
	driver = rm.open_resource(usb[0], timeout=10000, chunk_size=102400) 
	scope = MyScope(driver=driver)
	print(scope)
		
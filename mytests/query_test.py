import unittest
import time
from Oscilloscope import MyScope
import numpy as np
import matplotlib.pyplot as plt
import sys
import visa


class ScopeTests(unittest.TestCase):

	def setUp(self):
		rm = visa.ResourceManager()
		# Get the USB device, e.g. 'USB0::0x1AB1::0x0588::DS1ED141904883'
		instruments = rm.list_resources()
		usb = list(filter(lambda x: 'USB' in x, instruments))
		if len(usb) != 1:
			print('Bad instrument list', instruments)
			sys.exit(-1)	
		driver = rm.open_resource(usb[0], timeout=10000, chunk_size=10240000)
		self.scope = MyScope(driver=driver)
	
	def tearDown(self):
		self.scope.close()

	def test_get_sample_rate(self):
		print("\n")
		mem_depth = self.scope.query_memdepth()
		print(mem_depth)
		assert mem_depth == 280000
		self.scope.query_sample_rate()
		self.scope.query_horiz_timebase()
		
		data = self.scope.query_ascii_data_singlebatch(channel=1, mode='RAW', fmt='ASCII', pstart=1, pend=100)
		assert data is not None
		plt.plot(data)
		plt.show()
		print(len(data))
		#self.scope.save_waveform_csv(usb_loc='FRONT', file_name='scopeout1.csv')
		
	def test_status_methods(self):
		print("Status", self.scope.query_isfinished())

	
	
#if __name__ == "__main__":
#	unittest.main()
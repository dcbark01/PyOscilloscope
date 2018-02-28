"""
** NOTE: TODO - STILL HAVING ISSUES WITH THIS SCRIPT, 
THE SCOPE SEEMS TO TIME OUT WHEN WRITING THE DATA TO CSV


@author: Daniel Barker


To run this code:
1. Activate RigolScope environment
	$ cd myAnaconda/envs/RigolScope
	$ activate RigolScope
	$ cd Scope
	
2. Run the script (example):
	$ python scope2csv.py -f="test1.csv" -d dataout
	
""" 

import time
import argparse
import string
import json
from Oscilloscope import MyScope
import visa


def get_parser():
	"""Get parser for command line arguments. """
	parser = argparse.ArgumentParser(description="Rigol Oscilloscope CSV Capture")
	parser.add_argument("-f", "--filename", dest="filename", help="Filename/Filter")
	parser.add_argument("-d", "--data-dir", dest="data_dir", help="Output/Data Directory")
	parser.add_argument("-u", "--usb-loc", dest="usb_loc", default="FRONT")
	parser.add_argument("-dn", "--device-number", dest="device_number", default=0)
	parser.add_argument("-cs", "--chunk-size", dest="chunk_size", default=10240000)
	parser.add_argument("-t", "--time-out", dest="time_out", default=10000)
	return parser


class MyScopeCapture(MyScope):
	""" Custom Oscilloscope class for capturing waveform data to csv """
	
	def __init__(self, driver, data_dir, filename):
		super().__init__(self)
		self.filename = filename
		self.outfile = data_dir + '/' + filename
		self.driver = driver
	
	def scope2csv(self, usb_loc, file_name):
		self.save_waveform_csv(usb_loc, file_name)
		

@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status

if __name__ == '__main__':

	# Get parser and args
	parser = get_parser()
	args = parser.parse_args()

	# Setup a scope instance
	rm = visa.ResourceManager()
	# Get the USB device, e.g. 'USB0::0x1AB1::0x0588::DS1ED141904883'
	instruments = rm.list_resources()
	usb = list(filter(lambda x: 'USB' in x, instruments))
	if len(usb) != 1:
		print('Bad instrument list', instruments)
		sys.exit(-1)	
	driver = rm.open_resource(usb[args.device_number], timeout=args.time_out, chunk_size=args.chunk_size)
	scope = MyScopeCapture(driver=driver, data_dir=args.data_dir, filename=args.filename)

	# Save csv file to USB drive
	# scope.save_waveform_csv(args.usb_loc, file_name=scope.outfile)
	scope.scope2csv(args.usb_loc, file_name=scope.outfile)
	#time.sleep(30)
	
import uproot
import glob
import datetime
import matplotlib.dates as dates
import ROOT

class rootreader:
	def __init__(self, fname, mask=None):
		f = uproot.open(fname) #returns a ROOT Directory, which behaves like a py dictionary
		tree = f['output'] #accesses a root tree stored in 'output'
		self.bobs = tree.keys() #instance has attributes ("bobs") equal to the keys in tree
		if mask is None:
			self.obs = [p.decode('utf-8') for p in self.bobs] #the attribute obs are the atributes of bobs, but converted to strings python can understand
		else:
			self.obs = mask #an exception made, if there is a mask you'd like to use
		if 'uTDays' not in self.obs:
			self.obs.append('uTDays')
		if 'uTSecs' not in self.obs:
			self.obs.append('uTSecs')
		ev = tree.arrays(self.obs) #get arrays of values for each attribute (there is a value for each event); Now, each attribute is a key with an array of values. 
		test = tree.arrays((self.obs)[0])
		for obs in self.obs: #for an attribute in this list
			setattr(self, obs, ev[obs.encode('utf-8')]) #Key = attribute or leaf in root tree, and the value is an array of values, one for each event
		self.start_time = self.uTDays[0] + self.uTSecs[0]/3600/24
		self.end_time = self.uTDays[-1] + self.uTSecs[-1]/3600/24
		self.run_length = self.end_time - self.start_time

		snop_epoch = dates.date2num(datetime.date(2010,1,1))
		self.real_time = dates.num2date(snop_epoch + self.start_time)

	def keys(self):
		return self.obs 


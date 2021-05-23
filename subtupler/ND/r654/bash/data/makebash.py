import os
import sys
import numpy as np

#runs = 3 
#uncomment above line to test small batch
BATCH_NAME = 'ND_int_data_subs'
JOB_NAME = 'ND_int_data_subs'
DATA_PATH = '/nfs/disk0/dgooding2/FullDCPush_DataAndCalibration_Preprocessing/N16/r654/data/full/int/'
SCRIPT_PATH = '/nfs/disk0/dgooding2/FullDCPush_DataAndCalibration_Preprocessing/subtupler/ND/r654/'
SCRIPT_NAME = 'subtupleMaker_Analysis'
OUTPATH = '/nfs/disk0/dgooding2/FullDCPush_DataAndCalibration_Preprocessing/N16/r654/data/subtupled/int'


input_file_list = [file for file in os.listdir(DATA_PATH)]
runs = len(input_file_list)

g = open('slurm.sh', 'a')
g.write('#!/bin/bash')
g.write('\n')
chonkies = list(np.arange(50, 100, 50))
for i in range(runs):
	name = 'batch_{}_{}.sh'.format(BATCH_NAME, i)
	f = open(name, 'a')
	f.write('#!/bin/bash')
	f.write('\n')
	f.write('#SBATCH -J {}'.format(JOB_NAME))
	f.write('\n')
	f.write('#SBATCH -t 23:00:00')
	f.write('\n')
	datapath = str(DATA_PATH + input_file_list[i])
	f.write('source /proj/common/sw/geant4/10.00.p02/bin/geant4.sh')
	f.write('\n')
	f.write('source /proj/common/sw/root/5.34.34/bin/thisroot.sh')
	f.write('\n')
	f.write('source /home/dgooding2/rat/env.sh')
	f.write('\n')
	f.write('mkdir {}/dir_{}'.format(OUTPATH, i))
	f.write('\n')
	f.write('cd {}'.format(SCRIPT_PATH))
	f.write('\n')
	outname = '{}/dir_{}/out_{}.root'.format(OUTPATH, i, i) 
	f.write('./{} --data {} --out {}'.format(SCRIPT_NAME, datapath, outname))
	f.write('\n')
	f.close()
	g.write('sbatch {}'.format(name))
	g.write('\n')
	if i in chonkies:
		g.write('squeue -u dgooding2 >> stuff')
		g.write('\n')
		g.write('while [ $(wc -l <stuff) -ge 50 ]')
		g.write('\n')
		g.write('do')
		g.write('\n')
		g.write('	rm stuff')
		g.write('\n')
		g.write('	sleep 20s')
		g.write('\n')
		g.write('	squeue -u dgooding2 >> stuff')
		g.write('\n')
		g.write('done')
		g.write('\n')
		g.write('rm stuff')
		g.write('\n')

g.close()

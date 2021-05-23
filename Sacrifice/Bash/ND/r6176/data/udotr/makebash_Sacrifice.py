import os
import sys
import numpy as np

runs = 144
BATCH_NAME = 'ND'
JOB_NAME = 'ND_data_sac_udotr'
DATA_PATH = '/nfs/disk0/dgooding2/FullDCPush_N16_2021March16/r6176/data/subtupled/int/ND/'
SCRIPT_PATH = '/home/dgooding2/BigDCTest_waterphase_2020Nov30/Sacrifice/scripts/AccFill/ND/data/'
SCRIPT_NAME = '/home/dgooding2/BigDCTest_waterphase_2020Nov30/Sacrifice/scripts/AccFill/ND/data/AllSac_udotr.py'


g = open('slurm.sh', 'a')
g.write('#!/bin/bash')
g.write('\n')
chonkies = list(np.arange(2, 100, 50))
for i in range(runs):
	name = 'batch_{}_{}.sh'.format(BATCH_NAME, i)
	f = open(name, 'a')
	f.write('#!/bin/bash')
	f.write('\n')
	f.write('#SBATCH -J {}'.format(JOB_NAME))
	f.write('\n')
	f.write('#SBATCH -t 23:00:00')
	f.write('\n')
	datapath = str(DATA_PATH + 'dir_{}/'.format(i))
	f.write('source /proj/common/sw/geant4/10.00.p02/bin/geant4.sh')
	f.write('\n')
	f.write('source /proj/common/sw/root/5.34.34/bin/thisroot.sh')
	f.write('\n')
	f.write('source /home/dgooding2/rat/env.sh')
	f.write('\n')
	f.write('cd {}'.format(SCRIPT_PATH))
	f.write('\n')
	outname = '/home/dgooding2/BigDCTest_waterphase_2020Nov30/Sacrifice/outroots/ND/data/udotr/out_{}.root'.format(i)
	f.write('python {} {} {}'.format(SCRIPT_NAME, datapath, outname))
	f.write('\n')
	f.close()
	g.write('sbatch {}'.format(name))
	g.write('\n')
	if i in chonkies:
		g.write('squeue -u dgooding2 >> stuff')
		g.write('\n')
		g.write('while [ $(wc -l <stuff) -ge 100 ]')
		g.write('\n')
		g.write('do')
		g.write('\n')
		g.write('	rm stuff')
		g.write('\n')
		g.write('	sleep 10s')
		g.write('\n')
		g.write('	squeue -u dgooding2 >> stuff')
		g.write('\n')
		g.write('done')
		g.write('\n')
		g.write('rm stuff')
		g.write('\n')

g.close()

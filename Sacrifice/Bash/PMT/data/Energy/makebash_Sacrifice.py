import os
import sys
import numpy as np

runs = 144
BATCH_NAME = 'PMT'
JOB_NAME = 'PMT_data_sac_Energy'
DATA_PATH = '/nfs/disk0/dgooding2/new_BatchSubmission_Subtupler/NewSubs_newEcorr/N16_Data_ext_subs/'
SCRIPT_PATH = '/nfs/disk2/dgooding2/Sacrifice_test/Release_1/Sacrifice/scripts/AccFill/PMT/data/'
SCRIPT_NAME = '/nfs/disk2/dgooding2/Sacrifice_test/Release_1/Sacrifice/scripts/AccFill/PMT/data/AllSac_Energy.py' 


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
	outname = '/nfs/disk2/dgooding2/Sacrifice_test/Release_1/Sacrifice/outroots/PMT/data/Energy/out_{}.root'.format(i)
	f.write('python {} {} {}'.format(SCRIPT_NAME, datapath, outname))
	f.write('\n')
	f.close()
	g.write('sbatch {}'.format(name))
	g.write('\n')
#	if i in chonkies:
#		g.write('squeue -u dgooding2 >> stuff')
#		g.write('\n')
#		g.write('while [ $(wc -l <stuff) -ge 100 ]')
#		g.write('\n')
#		g.write('do')
#		g.write('\n')
#		g.write('	rm stuff')
#		g.write('\n')
#		g.write('	sleep 10s')
#		g.write('\n')
#		g.write('	squeue -u dgooding2 >> stuff')
#		g.write('\n')
#		g.write('done')
#		g.write('\n')
#		g.write('rm stuff')
#		g.write('\n')

g.close()

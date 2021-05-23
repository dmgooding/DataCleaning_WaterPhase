import os
import sys
import numpy as np

#runs = 3 
#uncomment above line to test small batch
BATCH_NAME = 'timebin1'
JOB_NAME = 'DC_Diana_cont'
#DATA_PATH ='/nfs/disk0/dgooding2/FullDCPush_N16_2021March16/TB1/blind/'
DATA_PATH ='/nfs/disk1/nd_analysis_final_dataset/'
SCRIPT_PATH = '/nfs/disk0/dgooding2/FullDCPush_N16_2021March16/subtupler/ND/'
SCRIPT_NAME = 'subtupleMaker_Analysis'
OUTPATH = '/nfs/disk0/dgooding2/WaterSubs_6_17_6'

CONT_PATH = '/nfs/disk0/dgooding2/WaterSubs_6_17_6/'
CONT_SCRIPT = 'cont_res_lt200000.py'
CONT_OUTPATH = '/nfs/disk0/dgooding2/WaterSubs_6_17_6/Bifur_txt'


input_file_list = [file for file in os.listdir(DATA_PATH)]
runs = len(input_file_list)

g = open('slurm.sh', 'a')
g.write('#!/bin/bash')
g.write('\n')
chonkies = list(np.arange(100, 15000, 100))
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
	contname = '{}/bifur_{}.txt'.format(CONT_OUTPATH, i)
	f.write('cd {}'.format(CONT_PATH))
	f.write('\n')
	f.write('python {} {}/dir_{}/ {} vest_flag'.format(CONT_SCRIPT, OUTPATH, i, contname))
	f.write('\n')
	f.write('rm -rf {}/dir_{}'.format(OUTPATH,i))
	f.close()
	g.write('sbatch {}'.format(name))
	g.write('\n')
	if i in chonkies:
		g.write('squeue >> stuff')
		g.write('\n')
		g.write('while [ $(wc -l <stuff) -ge 2000 ]')
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

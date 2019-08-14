#!/usr/bin/python
import sys
from os import getcwd, mkdir, chdir, system, remove
from os.path import exists

### SCRIPT TO SUBMIT MULTIPLE REPS OF A BEAST JOB AT THE UCT HPC. ###
### EXECUTE SCRIPT FROM WITHIN XML DIRECTORY, WHERE BEAST OUTPUT WILL BE WRITTEN TO. ###
### USAGE: script_name.py <filename.xml> <Job_name: Max 10 characters> <number_of_reps> <Processor: CPU> ###
### eg.  script_name.py <filename.xml> <job_name> <-5> <-cpu> ###


def make_directory(name):		# First checks to see if directory exists, and if not creates a directory.
	if not exists(name):
		mkdir(name)


def run_on_CPU(rep, cur_dir, jobname, xml_filename, email):	# Function to create temporary shell script to qsub onto dell cluster. 
	tmp_output_file = open('tmp_submit_script.sh', 'w')
	tmp_output_string = '''#!/bin/sh
	
#SBATCH --job-name="%s_R%s"
#SBATCH --nodes=1 --ntasks=40
#SBATCH --account=icts
#SBATCH --partition=ada
#SBATCH --time=10:00:00
#SBATCH -o %s/rep%s/std.out
#SBATCH -e %s/rep%s/std.err
#SBATCH --mail-user=%s
#SBATCH --mail-type=ALL

cd %s/rep%s
module load software/beast-1.10.4

java -Xms25600m -Xmx51200m -jar -XX:+UseSerialGC -Djava.library.path="$BEAST_LIB_PATH:/opt/exp_soft/beagle-lib/lib"

/opt/exp_soft/BEASTv1.8.2/bin/beast -overwrite -beagle -beagle_sse -beagle_scaling always  %s/%s
''' % (jobname, rep, cur_dir, rep, cur_dir, rep, email, cur_dir, rep, cur_dir, xml_filename)

	tmp_output_file.write(tmp_output_string)
	tmp_output_file.close()








if len(sys.argv) < 5:
	sys.stderr.write('\nIncorrect number of arguments. '
						'Usage: script_name.py <filename.xml> '
						'<Job_name: Max 10 characters> <number_of_reps> <Processor: CPU>\n\n')
	sys.exit(1)

xml_filename = sys.argv[1]

jobname = sys.argv[2]
if len(jobname) >= 10:
	jobname = jobname[:10]

num_reps = sys.argv[3]
if num_reps.startswith('-'):
	num_reps = num_reps[1:]

proc_flag = sys.argv[4]
if proc_flag.startswith('-'):
	proc_flag = proc_flag[1:].lower()
else:
	proc_flag = proc_flag[:].lower()


cur_dir = getcwd()			# Option so that script can be used by anyone.
email = input('\nEnter email address for job notifications: ')
print('\n')


# Creates replicate runs directories and executes shell scripts to run BEASTv1.8.1 in queue.
for rep in range(1, int(num_reps) + 1):
	rep_name = 'rep' + str(rep)
	make_directory(rep_name)
	run_on_CPU(rep, cur_dir, jobname, xml_filename, email)
	system('sbatch tmp_submit_script.sh')
	remove('tmp_submit_script.sh')


print('\nScript done...\n')

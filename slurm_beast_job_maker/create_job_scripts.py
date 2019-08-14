import argparse
import os
import sys


def make_directory(name):  # First checks to see if directory exists, and if not creates a directory.
    if not os.path.exists(name):
        os.mkdir(name)


# Function to create temporary shell script to qsub onto dell cluster.
def run_on_CPU(rep, cur_dir, jobname, xml_filename, email):
    tmp_output_file = open('tmp_submit_script.sh', 'w')
    tmp_output_string = '''#!/bin/sh

#SBATCH --job-name="{jobname}_R{rep}"
#SBATCH --nodes=1 --ntasks=40
#SBATCH --account {account}
#SBATCH --partition=ada
#SBATCH --time=10:00:00
#SBATCH -o {}/rep{}/std.out
#SBATCH -e {}/rep{}/std.err
#SBATCH --mail-user={email}
#SBATCH --mail-type=ALL

cd {}/rep{}
module load software/beast-1.10.4

java -Xms25600m -Xmx51200m -jar -XX:+UseSerialGC -Djava.library.path="$BEAST_LIB_PATH:/opt/exp_soft/beagle-lib/lib"

/opt/exp_soft/BEASTv1.8.2/bin/beast -overwrite -beagle -beagle_sse -beagle_scaling always  %s/{xml_filename}
''' % (jobname, rep, cur_dir, rep, cur_dir, rep, email, cur_dir, rep, cur_dir, xml_filename)

    tmp_output_file.write(tmp_output_string)
    tmp_output_file.close()


def main(inXML, email, job_name, wd, numRepeats):

    for rep in range(1, numRepeats + 1):
        rep_name = 'repeat_' + str(rep)
        repeat_working_dir = os.path.join(wd, rep_name)

        make_directory(rep_name)
        run_on_CPU(rep, cur_dir, job_name, inXML, email)
        system('sbatch tmp_submit_script.sh')
        remove('tmp_submit_script.sh')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python script to create slurm job submission scripts, for BEAST'
                                                 'jobs to be run on HPC at UCT.'
                                                 'http://hpc.uct.ac.za/')
    parser.add_argument('-inXML', '--inXML', type=str,
                        help='input XML file which is created from BEAUTI and contains all BEAST '
                             'properties', required=True)
    parser.add_argument('-jn', '--jobname', type=str,
                        help='The name of the job. Max of 10 characters', required=True)

    parser.add_argument('-e', '--email', type=str,
                        help='The email address to send a notification to once the job is completed, or error '
                             'occur', required=True)
    parser.add_argument('-proc', '--processor', type=str,
                        help='The type of processor to use, either CPU or.... ', required=True)
    parser.add_argument('-nr', '--numRepeats', type=int,
                        help='The name of repeats to perform.', required=True)
    parser.add_argument('-wd', '--workingDirectory', type=str,
                        help='The directory where you want all your output to go to', required=True)

    args = parser.parse_args()
    inXML = args.inXML
    job_name = args.jobname
    email = args.email
    proc = args.proc
    numRepeats = args.numRepeats
    wd= args.workingDirectory

    if len(job_name) > 10:
        print("Please reduce your jobname to be 10 or less characters. Now exiting")
        sys.exit()

    # proc = proc,
    main(inXML=inXML, email=email, job_name=job_name, wd=wd, numRepeats=numRepeats)

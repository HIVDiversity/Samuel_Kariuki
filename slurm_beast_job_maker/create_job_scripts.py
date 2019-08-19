import argparse
import os
import sys
import subprocess


# Function to create temporary shell script to qsub onto dell cluster.
def write_script_and_call(repeatNumber, jobname, account, working_dir, email, xml_filename):
    slurm_script_filename = 'slurm_script_repeat_{repeatNumber}.sh'.format(repeatNumber=repeatNumber)
    with open(slurm_script_filename, 'w') as file_writer:
        tmp_output_string = '''#!/bin/sh
#SBATCH --job-name="{jobname}_R{repeatNumber}"
#SBATCH --nodes=1 --ntasks=40
#SBATCH --account {account}
#SBATCH --partition=ada
#SBATCH --time=10:00:00
#SBATCH -o {working_dir}/std.out
#SBATCH -e {working_dir}/std.err
#SBATCH --mail-user={email}
#SBATCH --mail-type=ALL

cd {working_dir}
module load software/beast-1.10.4

java -jar -Djava.library.path=/opt/exp_soft/beagle-lib/lib/ /opt/exp_soft/BEASTv1.10.4/lib/beast.jar {xml_filename}
'''.format(jobname=jobname, repeatNumber=repeatNumber, account=account,
           working_dir=working_dir, email=email, xml_filename=xml_filename)

        file_writer.write(tmp_output_string)

    subprocess.call('tmp_submit_script.sh')


def main(inXML, email, job_name, proc, wd, numRepeats, account):

    for repeatNumber in range(1, numRepeats + 1):
        repeatName = 'repeat_' + str(repeatNumber)
        repeat_working_dir = os.path.join(wd, repeatName)
        if not os.path.exists(repeat_working_dir):
            os.mkdir(repeat_working_dir)

        write_script_and_call(repeatNumber, job_name, account, repeat_working_dir, email, inXML)


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
    parser.add_argument('-a', '--account', type=str, help="The registered users account name on HPC at UCT. Examples "
                                                          "include math / pathology / music. etc.")

    args = parser.parse_args()
    inXML = args.inXML
    email = args.email
    job_name = args.jobname
    proc = args.processor
    numRepeats = args.numRepeats
    wd = args.workingDirectory
    account = args.account

    if len(job_name) > 10:
        print("Please reduce your jobname to be 10 or less characters. Now exiting")
        sys.exit()

    main(inXML=inXML, email=email, job_name=job_name, proc=proc, numRepeats=numRepeats, wd=wd, account=account)

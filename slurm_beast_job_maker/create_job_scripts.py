import argparse
import os
import sys
import subprocess

#                       job_name, account, wd,          email, repeat_dirs,         inXML

# Function to call multiple bash scripts in parallel on SLURM under a single slurm resource aquisition.
def call_all_in_parallel(jobname, account, working_dir, email, list_of_dirs_for_cd, inXML):
    slurm_script_filename = os.path.join(working_dir, 'slurm_script.sh')
    std_out_fn = os.path.join(working_dir, "std.out")
    std_err_fn = os.path.join(working_dir, "std.err")
    with open(slurm_script_filename, 'w') as file_writer:
        tmp_output_string = '''#!/bin/sh
#SBATCH --job-name="{jobname}"
#SBATCH --nodes=1 --ntasks=40
#SBATCH --account {account}
#SBATCH --partition=ada
#SBATCH --time=10:00:00
#SBATCH -o {std_out_fn}
#SBATCH -e {std_err_fn}
#SBATCH --mail-user={email}
#SBATCH --mail-type=ALL


module load software/beast-1.10.4

'''.format(jobname=jobname, account=account, working_dir=working_dir,
           email=email, std_out_fn=std_out_fn, std_err_fn=std_err_fn)

        for cd_dir in list_of_dirs_for_cd:
            tmp_output_string += """"

cd {cd_dir}
java -jar -Djava.library.path=/opt/exp_soft/beagle-lib/lib/ /opt/exp_soft/BEASTv1.10.4/lib/beast.jar {inXML} &

            """.format(cd_dir=cd_dir, inXML=inXML)

        try:
            file_writer.write(tmp_output_string)
        except Exception as e:
            print(e)
            return False

    std_err_fn, std_out_fn = os.path.join(working_dir, "std_error.log"), os.path.join(working_dir, "std_out.log")
    std_err = open(std_err_fn, "w")
    std_out = open(std_out_fn, "w")
    try:
        subprocess.call("sbatch " + slurm_script_filename, shell=True, stderr=std_err, stdout=std_out)
    except Exception as e:
        print(e)
        return False


def main(inXML, email, job_name, proc, wd, numRepeats, account):

    repeat_dirs = []
    for repeatNumber in range(1, numRepeats + 1):
        repeatName = 'repeat_' + str(repeatNumber)  # repeat_1, repeat_2...etc
        repeat_working_dir = os.path.join(wd, repeatName)  # /home/dmatten/Sam_beast/job_directory/repeat_1/
        if not os.path.exists(repeat_working_dir):
            os.mkdir(repeat_working_dir)
        repeat_dirs.append(repeat_working_dir)

    call_all_in_parallel(job_name, account, wd, email, repeat_dirs, inXML)


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

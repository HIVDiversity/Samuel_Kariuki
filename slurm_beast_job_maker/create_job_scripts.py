import argparse
import os
import sys
import subprocess


# Function to call multiple bash scripts in parallel on SLURM under a single slurm resource aquisition.
def call_all_in_parallel(jobname, account, working_dir, email, list_of_files_to_call):
    slurm_script_filename = os.path.join(working_dir, 'slurm_script.sh')
    with open(slurm_script_filename, 'w') as file_writer:
        tmp_output_string = '''#!/bin/sh
#SBATCH --job-name="{jobname}"
#SBATCH --nodes=1 --ntasks=40
#SBATCH --account {account}
#SBATCH --partition=ada
#SBATCH --time=10:00:00
#SBATCH -o {working_dir}/std.out
#SBATCH -e {working_dir}/std.err
#SBATCH --mail-user={email}
#SBATCH --mail-type=ALL

'''.format(jobname=jobname, account=account, working_dir=working_dir, email=email)

        for bashscript_fn in list_of_files_to_call:
            tmp_output_string += "{bashscript_fn} &".format(bashscript_fn=bashscript_fn)

        try:
            file_writer.write(tmp_output_string)
        except Exception as e:
            print(e)
            return False

    std_err_fn, std_out_fn = os.path.join(working_dir, "std_error.log"), os.path.join(working_dir, "std_out.log")
    std_err = open(std_err_fn, "w")
    std_out = open(std_out_fn, "w")
    try:
        subprocess.call("bash " + slurm_script_filename, shell=True, stderr=std_err, stdout=std_out)
    except Exception as e:
        print(e)
        return False


def write_sh(filename_to_write_to, xml_filename):
    file_content = """
module load software/beast-1.10.4
java -jar -Djava.library.path=/opt/exp_soft/beagle-lib/lib/ /opt/exp_soft/BEASTv1.10.4/lib/beast.jar {xml_filename}    
    """.format(xml_filename=xml_filename)
    try:
        with open(filename_to_write_to, "w") as fw:
            fw.write(file_content)
        return True
    except Exception as e:
        print(e)
        return False


def main(inXML, email, job_name, proc, wd, numRepeats, account):

    script_filenames = []
    for repeatNumber in range(1, numRepeats + 1):
        repeatName = 'repeat_' + str(repeatNumber)
        repeat_working_dir = os.path.join(wd, repeatName)
        if not os.path.exists(repeat_working_dir):
            os.mkdir(repeat_working_dir)
        sh_fn = os.path.join(repeat_working_dir + ".sh")
        write_sh(sh_fn, inXML)
        script_filenames.append(sh_fn)

    call_all_in_parallel(job_name, account, repeat_working_dir, email, script_filenames)


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

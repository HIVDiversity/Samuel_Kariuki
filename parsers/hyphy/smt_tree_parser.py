import sys
import os
import argparse


def main(indir, outpath):
    print("The input directory is: ", indir)
    print("The output directory is: ", outpath)

    # There are meant to be 1000 files in the indir.
    # We read each in order, and extract a bit from each, appending to a list.
    # once we have finished, we write all the list content to a .csv file in the outpath.

    inferred, prob = [], []
    for root, dirs, files in os.walk(indir):
        break
    for fn in files:
        fn = os.path.join(root, fn)
        # print(fn)
        with open(fn, "r") as fh:
            for line in fh:
                # print(line)
                if line[:8] == "Inferred":
                    inferred.append(line.split(" ")[1])
                if line[:51] == "Prob{as many or fewer migration events by chance} =":
                    prob.append(line.strip().split("=")[-1])
        # print("inferred: ")
        # print(inferred)
        # print("prob: ")
        # print(prob)
        # r = input("Next?")
    out_fn = os.path.join(outpath, "out.csv")
    with open(out_fn, "w") as fw:
        fw.write("inferred, prob\n")
        for inf, prb in zip(inferred, prob):
            fw.write("{}, {}\n".format(inf, prb))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='a script to parse output from hyphy')

    parser.add_argument('-indir', '--indir', type=str,
                        help='The input directory to all the 1000 files.', required=True)
    parser.add_argument('-out_dir', '--out_dir', type=str,
                        help='The output directory where you want the out.csv file to be written. Just a directory - no '
                             'filename. output file will be named: out.csv ', required=True)

    args = parser.parse_args()
    indir = args.indir
    outpath = args.out_dir

    if not os.path.exists(indir):
        print("It looks like input directory doesn't exist")
        sys.exit()
    if not os.path.exists(outpath):
        print("It looks like outpath doesn't exist")
        sys.exit()

    main(indir, outpath)


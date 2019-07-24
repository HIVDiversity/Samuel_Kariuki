import argparse


def main(infile):
    print("Doing main stuff")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='some program description')
    parser.add_argument('-in', '--infile', type=str,
                        help='some helpful help text', required=True)

    args = parser.parse_args()
    infile = args.infile

    main(infile)

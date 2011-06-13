import argparse


args = None


def parse_args(desc):
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--config', '-c', help='The path to the config file')
    args = parser.parse_args()
    return args

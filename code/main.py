from tools.data_tools import data_processing
from tools.rec_tools import rec_sys
import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flip a switch by setting a flag")
    parser.add_argument(
        '-d', help="data ingestion and processing step", action='store_true')
    parser.add_argument(
        '-t', help="Rec Sys fitting and outputs recommendations", action='store_true')
    parser.add_argument(
        '-e', help="Evaluation of the current Rec Sys parameters", action='store_true')
    

    args = parser.parse_args()

    if args.d:
        data_processing()
    
    if args.t:
        rec_sys(evaluation=args.e)
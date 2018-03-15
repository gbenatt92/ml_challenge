from tools.data_tools import data_processing
from tools.rec_tools import rec_sys
import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flip a switch by setting a flag")
    parser.add_argument(
        '-d', help="data ingestion and processing step", action='store_true')
    parser.add_argument(
        '-t', help="data ingestion and processing step", action='store_true')

    args = parser.parse_args()

    if args.d:
        data_processing()
    
    if args.t:
        rec_sys()
# docker run -it -v /home/gabrielalvim/Documents/ml_challenge/data:/data_proj -v `pwd`:/app  --entrypoint bash gbenatt92/ml-challenge-ingestion:latest

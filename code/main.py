from tools.data_tools import data_processing
import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flip a switch by setting a flag")
    parser.add_argument(
        '-d', help="data ingestion and processing step", action='store_true')

    args = parser.parse_args()

    if args.d:
        data_processing()
# docker run -it -v /home/gabrielalvim/Documents/ml_challenge/data:/data_proj -v `pwd`:/app  --entrypoint bash gbenatt92/ml-challenge-ingestion:latest

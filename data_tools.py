import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import json
import lzma


def append_to_parquet_file(dataframe, filepath=None, writer=None):
    """ Appending to dataframe parquet file.
    If writer is none, a new writer is created using the table path.

    Parameters
    ----------
    dataframe: {pandas datasetframe} shape(n,m)
        Pandas dataframe table.
    filepath: {string}
        Path string where the parquet file will be created.
    writer: {object}
        Pyarrow writer object to save a parquet file.

    Returns
    -------
    writer: {object}
        Pyarrow writer object to save a parquet file.
    """
    table = pa.Table.from_pandas(dataframe)
    if writer is None:
        writer = pq.ParquetWriter(filepath, table.schema, compression='snappy')
    writer.write_table(table=table)
    return writer


def product_to_string(json_line):
    """Concatenates product ids to string.
    This is done so we can easily calculate products purchased per person.
    
    Parameters
    ----------
    json_line: {dict}
        Dictionary corresponding to a json line from the ndjson file.
    
    Returns
    ----------
    json_line: {dict}
        Dictionary with the field items replaced by the concatenation of product_id.
    
    """
    json_line['items'] = [i['product_id']
                          for i in json_line['items']]
    json_line['items'] = '|'.join(json_line['items'])
    return json_line

def ndjson_line_to_parquet(line,writer,output_file_path,items=False):
    """Appends a line from the uncompressed ndjson file to a parquet file.

    Parameters
    ----------
    line: {TextIO object}
        Text object for a line from the ndjson file.
    writer: {object}
        Pyarrow writer object to save a parquet file.
    output_file_path: {string}
        Path string where the parquet file will be created.
    items: {bool}
        Bool that indicates if the product_to_string passes or not.
    
    Returns
    -------
    writer: {object}
        Pyarrow writer object to save a parquet file.
    """
    json_l = json.loads(line)
    if items:
        json_l = product_to_string(json_l)
    df = pd.DataFrame(json_l, index=[0])
    return append_to_parquet_file(
        df, output_file_path, writer=writer)



def xz_ndjson_to_parquet(input_file_path, output_file_path, items=False):
    """ Reading compressed ndjson and writing to a parquet file.
    Make sure to load and decompress ndjson.xz in a stream manner.

    Parameters
    ----------
    input_file_path: {string}
        Path string where the ndjson.xz file is located.
    output_file_path: {string}
        Path string where the parquet file will be created.
    """
    with open(input_file_path, "rb") as compressed:
        with lzma.LZMAFile(compressed) as uncompressed:
            writer = None
            i = 0
            k= 10000
            for line in uncompressed:
                # Data frame is used for easy conversion.
                writer = ndjson_line_to_parquet(line,writer,output_file_path,items)
                i += 1
                if i % k == 0:
                    print(i)
                    writer.close()
                    writer = None

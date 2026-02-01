#!/usr/bin/env python

import click
import requests
import bz2
from pathlib import Path

def download_file(url, dest_folder):
    """
    Download the file from the given URL and save it in the destination folder.
    """
    filename = url.split("/")[-1]
    dest_path = dest_folder/filename

    # Make request and download the file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, "wb") as fd:
            for chunk in response.iter_content(chunk_size=1024):
                fd.write(chunk)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download {url}")
        return None
    return dest_path

def decompress_bz2(bz2_file_path, output_folder):
    """
    Decompress a bz2 file and store the result in the output folder.
    """
    output_file_path = output_folder/bz2_file_path.stem
    with bz2.BZ2File(bz2_file_path, "rb") as fd:
        with open(output_file_path, "wb") as output_file:
            output_file.write(fd.read())
        print(f"Decompressed: {output_file_path}")
        return output_file_path

@click.command()
@click.argument("urls", nargs=-1)  # Accept one or more URLs
@click.option("--output-dir", "-o", required=True, type=click.Path(), help="Directory to store (decompressed) files")
@click.option("--decompress", "-d", is_flag=True, help="Decompress the files")
def download_and_decompress(urls, output_dir, decompress):
    """
    Download and decompress .bz2 files from the specified URLs.
    """
    # Ensure output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each URL
    for url in urls:
        # Download the file
        bz2_file_path = download_file(url, output_dir)
        
        if bz2_file_path and decompress:
            # decompress the file
            decompress_bz2(bz2_file_path, output_dir)
            # Delete the .bz2 file after extraction
            bz2_file_path.unlink()

if __name__ == "__main__":
    download_and_decompress()

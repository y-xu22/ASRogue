import os
import gzip
import bz2
import shutil
import subprocess

INPUT_ROOT = "BGP RIB"

OUTPUT_ROOT = "BGP RIB txt"


def ensure_output_dir(input_path):
    rel_path = os.path.relpath(input_path, INPUT_ROOT)
    out_dir = os.path.join(OUTPUT_ROOT, os.path.dirname(rel_path))
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def decompress_file(path):
    if path.endswith(".gz"):
        out_path = path[:-3]
        with gzip.open(path, "rb") as f_in, open(out_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        return out_path

    elif path.endswith(".bz2"):
        out_path = path[:-4]
        with bz2.open(path, "rb") as f_in, open(out_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        return out_path

    return None


def run_bgpdump(mrt_file, txt_file):
    cmd = ["bgpdump", "-m", mrt_file]
    with open(txt_file, "w") as f_out:
        subprocess.run(cmd, stdout=f_out, text=True)


def process_all_files():
    for dirpath, _, filenames in os.walk(INPUT_ROOT):
        for filename in filenames:

            if not (filename.endswith("paths.gz") or filename.endswith("paths.bz2")):
                continue

            full_path = os.path.join(dirpath, filename)

            out_dir = ensure_output_dir(full_path)

            if filename.endswith(".gz"):
                mrt_file = full_path[:-3]
            else:
                mrt_file = full_path[:-4]

            txt_file = os.path.join(out_dir, os.path.basename(mrt_file) + ".txt")
            clean_txt_file = os.path.join(out_dir, os.path.basename(mrt_file) + ".clean.txt")

            if os.path.exists(txt_file):
                continue
            if os.path.exists(clean_txt_file):
                continue


            mrt_file = decompress_file(full_path)

            run_bgpdump(mrt_file, txt_file)

            os.remove(mrt_file)


if __name__ == "__main__":
    process_all_files()

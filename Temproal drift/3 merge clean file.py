import os

ROOT = "./BGP RIB txt"


def merge_clean_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):

        if dirpath == ROOT:
            continue

        clean_files = [f for f in filenames if f.endswith(".clean.txt")]
        if not clean_files:
            continue


        unique_lines = set()

        for fname in clean_files:
            full_path = os.path.join(dirpath, fname)

            with open(full_path, "r", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        unique_lines.add(line)

        folder_name = os.path.basename(dirpath)
        output_file = os.path.join(ROOT, f"{folder_name}.txt")


        with open(output_file, "w") as f_out:
            for line in sorted(unique_lines):
                f_out.write(line + "\n")



if __name__ == "__main__":
    merge_clean_files()

import os

INPUT_ROOT = "./BGP RIB txt"


def extract_as_path(line):
    parts = line.strip().split("|")
    if len(parts) >= 7:
        return parts[6] 
    return ""


def process_all_txt_files():
    for dirpath, _, filenames in os.walk(INPUT_ROOT):
        for filename in filenames:

            if filename.endswith(".clean.txt"):
                print(f"clean file already exists: {filename}")
                continue

            if not filename.endswith(".txt"):
                continue

            full_path = os.path.join(dirpath, filename)
            clean_path = full_path.replace(".txt", ".clean.txt")


            with open(full_path, "r", errors="ignore") as f_in, \
                 open(clean_path, "w") as f_out:

                for line in f_in:
                    as_path = extract_as_path(line)
                    if as_path:
                        f_out.write(as_path + "\n")

            os.remove(full_path)


if __name__ == "__main__":
    process_all_txt_files()

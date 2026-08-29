import os

PROJECT_FOLDER = r"C:\Users\sonib\StudioProjects\plant-disease-detector"
OUTPUT_FILE = os.path.join(PROJECT_FOLDER, "project_export.txt")

# Maximum file size to include completely.
# 0 = no limit.
MAX_FILE_SIZE = 0


def is_text_file(filepath):
    """
    Returns True if the file can reasonably be represented as text.
    This checks file content, not file extension.
    """
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)

        # Empty files are considered text files
        if not chunk:
            return True

        # Null bytes usually indicate binary content
        if b"\x00" in chunk:
            return False

        # Try UTF-8 decoding
        chunk.decode("utf-8")
        return True

    except Exception:
        return False


with open(OUTPUT_FILE, "w", encoding="utf-8") as output:

    output.write("# COMPLETE PROJECT EXPORT\n")
    output.write("# EVERYTHING POSSIBLE: FOLDER STRUCTURE + FILE CONTENTS\n")
    output.write("# NO DIRECTORIES OR FILES ARE INTENTIONALLY IGNORED\n\n")

    # ============================================================
    # PART 1: COMPLETE FOLDER AND FILE STRUCTURE
    # ============================================================

    output.write("=" * 100 + "\n")
    output.write("COMPLETE FOLDER STRUCTURE\n")
    output.write("=" * 100 + "\n\n")

    for root, dirs, files in os.walk(PROJECT_FOLDER):

        # Include ALL directories, including hidden ones
        relative_path = os.path.relpath(root, PROJECT_FOLDER)

        if relative_path == ".":
            output.write("plant-disease-detector/\n")
        else:
            level = relative_path.count(os.sep) + 1
            indent = "    " * level
            output.write(f"{indent}{os.path.basename(root)}/\n")

        for file in sorted(files):
            # Do not include the output file itself in the structure
            # otherwise the script will include its own growing output
            if os.path.abspath(os.path.join(root, file)) == os.path.abspath(OUTPUT_FILE):
                continue

            level = 1 if relative_path == "." else relative_path.count(os.sep) + 2
            indent = "    " * level
            output.write(f"{indent}{file}\n")


    # ============================================================
    # PART 2: COMPLETE FILE CONTENTS
    # ============================================================

    output.write("\n\n")
    output.write("=" * 100 + "\n")
    output.write("COMPLETE FILE CONTENTS\n")
    output.write("=" * 100 + "\n")

    for root, dirs, files in os.walk(PROJECT_FOLDER):

        # Do not ignore any directory

        for file in sorted(files):

            filepath = os.path.join(root, file)

            # Skip ONLY the output file itself
            # Otherwise the export would recursively export itself.
            if os.path.abspath(filepath) == os.path.abspath(OUTPUT_FILE):
                continue

            relative_filepath = os.path.relpath(
                filepath,
                PROJECT_FOLDER
            )

            output.write("\n\n")
            output.write("=" * 100 + "\n")
            output.write(f"FILE: {relative_filepath}\n")
            output.write(f"FULL PATH: {filepath}\n")

            try:
                file_size = os.path.getsize(filepath)
                output.write(f"SIZE: {file_size} bytes\n")
            except Exception:
                file_size = -1

            output.write("=" * 100 + "\n\n")

            # Check maximum file size
            if MAX_FILE_SIZE > 0 and file_size > MAX_FILE_SIZE:
                output.write(
                    f"[FILE NOT INCLUDED: Larger than "
                    f"{MAX_FILE_SIZE} bytes]\n"
                )
                continue

            # Try to read the file as text
            if is_text_file(filepath):

                try:
                    with open(
                        filepath,
                        "r",
                        encoding="utf-8",
                        errors="replace"
                    ) as f:

                        output.write(f.read())

                    output.write("\n")

                except Exception as e:
                    output.write(
                        f"[ERROR READING FILE AS TEXT: {e}]\n"
                    )

            else:
                # We cannot put arbitrary binary directly into a text file.
                # Record that it exists and its metadata.
                output.write(
                    "[BINARY FILE DETECTED]\n"
                )
                output.write(
                    "This file exists in the project but is not directly "
                    "representable as normal text.\n"
                )
                output.write(
                    "The filename, full path, and size are included above.\n"
                )

print("\n" + "=" * 70)
print("COMPLETE PROJECT EXPORT FINISHED!")
print(f"\nOutput file:\n{OUTPUT_FILE}")
print("\nEverything was scanned.")
print("No project folders or files were intentionally ignored.")
print("Binary files are recorded but cannot be directly written as")
print("normal source code into a text file.")
print("=" * 70)
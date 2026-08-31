import os

OUTPUT_FILE = "project_context.txt"

# Only pruned at the PROJECT ROOT (relative path == "./<name>"), never by bare
# name match at any depth. Previously "data" as a bare name also deleted the
# Android package folder mobile-app/app/src/main/java/com/kisanmitra/data/,
# which happens to share that name — silently hiding ApiClient.kt and the DTOs.
IGNORE_DIRS_AT_ROOT = {
    ".git", "venv", "__pycache__", "uploads", "data", "weights",
    ".pytest_cache", ".idea", ".vscode",
}

# These ARE safe to prune anywhere in the tree — they're build-tool caches by
# convention, not application source, so a name collision with real source
# code is not a realistic risk the way it is for a generic name like "data".
IGNORE_DIRS_ANYWHERE = {".gradle", "build", ".kotlin", "node_modules"}

IGNORE_FILES = {OUTPUT_FILE, "peekrakshak.db", "package-lock.json"}

ALLOWED_EXTENSIONS = {
    ".py", ".json", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".md",
    ".sql", ".env.example",
    ".kt", ".kts", ".xml",
}

def _prune_dirs(root, dirs):
    is_project_root = os.path.normpath(root) == "."
    if is_project_root:
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS_AT_ROOT and d not in IGNORE_DIRS_ANYWHERE]
    else:
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS_ANYWHERE]

def generate_context():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("=== PROJECT FOLDER STRUCTURE ===\n")
        for root, dirs, files in os.walk("."):
            _prune_dirs(root, dirs)
            level = root.replace(".", "").count(os.sep)
            indent = " " * 4 * level
            out.write(f"{indent}{os.path.basename(root)}/\n")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                if file not in IGNORE_FILES:
                    out.write(f"{sub_indent}{file}\n")

        out.write("\n\n=== FILE CONTENTS ===\n")
        for root, dirs, files in os.walk("."):
            _prune_dirs(root, dirs)
            for file in files:
                file_path = os.path.join(root, file)
                if file in IGNORE_FILES:
                    continue
                if not any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    continue

                out.write(f"\n\n--- FILE: {file_path} ---\n")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        out.write(f.read())
                except Exception as e:
                    out.write(f"[Error reading file: {e}]")

    print(f"Context file generated successfully: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_context()
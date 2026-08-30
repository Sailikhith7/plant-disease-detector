import os

OUTPUT_FILE = "project_context.txt"
IGNORE_DIRS = {".git", "venv", "__pycache__", "uploads", "data", "weights", ".pytest_cache", ".idea", ".vscode"}
IGNORE_FILES = {OUTPUT_FILE, "peekrakshak.db", "package-lock.json"}
ALLOWED_EXTENSIONS = {".py", ".json", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".md", ".sql", ".env.example"}

def generate_context():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("=== PROJECT FOLDER STRUCTURE ===\n")
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            level = root.replace(".", "").count(os.sep)
            indent = " " * 4 * level
            out.write(f"{indent}{os.path.basename(root)}/\n")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                if file not in IGNORE_FILES:
                    out.write(f"{sub_indent}{file}\n")
        
        out.write("\n\n=== FILE CONTENTS ===\n")
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
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
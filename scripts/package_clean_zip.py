import os
import zipfile

def create_clean_zip():
    source_dir = r"C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin"
    zip_path = r"C:\Users\pushpakalai\.gemini\antigravity\brain\9b4e34c5-0a17-4628-a67b-7f494a6650e9\smart_campus_digital_twin.zip"

    skip_dirs = {"venv", "node_modules", "__pycache__", ".git"}

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                if file.endswith('.pyc') or file == '.DS_Store':
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                try:
                    zipf.write(file_path, arcname)
                except Exception as e:
                    print(f"Skipping {arcname}: {e}")

    print(f"Clean ZIP successfully created at: {zip_path}")
    print(f"File size: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    create_clean_zip()

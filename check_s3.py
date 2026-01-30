import fsspec

def check_s3():
    try:
        fs = fsspec.filesystem("s3", anon=True)
        # Try to list a known path from the user's snippet
        # s3-radaresideam/l2_data/2022/08/09/Carimagua/
        files = fs.glob("s3-radaresideam/l2_data/2022/08/09/Carimagua/*")
        print(f"Found {len(files)} files.")
        if files:
            print(f"Sample: {files[0]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_s3()

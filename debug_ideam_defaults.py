
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from data_sources import ideam_radar

def debug_defaults():
    print("Debugging IDEAM Radar with App Defaults...")
    
    radar_name = "Carimagua"
    date_str = "2022/08/09"
    
    print(f"1. Listing files for {radar_name} on {date_str}...")
    files = ideam_radar.list_available_radar_files(date_str, radar_name)
    
    if not files:
        print("❌ No files found for default date/radar.")
    else:
        print(f"✅ Found {len(files)} files.")
        print(f"First file: {files[0]}")
        
        print("2. Attempting to plot first file...")
        try:
            fig = ideam_radar.create_radar_plot(files[0])
            if fig:
                print("✅ Plot created successfully.")
            else:
                print("❌ Plot creation returned None.")
        except Exception as e:
            print(f"❌ Plot creation raised exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_defaults()

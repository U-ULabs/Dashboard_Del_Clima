
import sys
import os
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from data_sources import ideam_radar

def verify_plot():
    print("Verifying Radar Plot Content...")
    
    # Use known available file
    radar_name = "Carimagua"
    date_str = "2022/08/09"
    
    files = ideam_radar.list_available_radar_files(date_str, radar_name, limit=1)
    if not files:
        print("❌ No files found.")
        return
        
    print(f"Plotting {files[0]}...")
    fig = ideam_radar.create_radar_plot(files[0])
    
    if fig:
        # Check title
        ax = fig.axes[0]
        title = ax.get_title()
        print(f"Plot Title: {title}")
        
        if "Reflectividad" in title:
            print("✅ Title contains 'Reflectividad'")
        else:
            print("⚠️ Title does NOT contain 'Reflectividad'")
            
        # Save for manual inspection if needed
        fig.savefig("radar_verification.png")
        print("Saved to radar_verification.png")
    else:
        print("❌ Failed to create plot.")

if __name__ == "__main__":
    verify_plot()

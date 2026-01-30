import sys
import os
# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from data_sources import ideam_radar

def test_ideam_module():
    print("Testing IDEAM Radar module...")
    
    print("\n1. Get radar locations:")
    df_radares = ideam_radar.get_radar_locations()
    print(df_radares)
    assert not df_radares.empty, "Radar locations DataFrame should not be empty"
    
    print("\n2. List available files (Guaviare, 2024/10/25):")
    # Using a known date/radar from previous exploration
    files = ideam_radar.list_available_radar_files("2024/10/25", "Guaviare", limit=3)
    
    if files:
        for f in files:
            print(f"  - {f}")
        
        print("\n3. Create radar plot (first file):")
        # We won't actually show the plot, just verify it returns a Figure
        fig = ideam_radar.create_radar_plot(files[0])
        if fig:
            print("  ✅ Plot created successfully")
            # Optional: save it
            # fig.savefig("test_plot_output.png")
        else:
            print("  ❌ Failed to create plot")
    else:
        print("  ⚠️ No files found to test plotting")

    print("\n✅ Module test complete!")

if __name__ == "__main__":
    test_ideam_module()

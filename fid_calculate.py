import os
import subprocess
import csv
from pathlib import Path

def calculate_fid(reference_path, comparison_path, device='cuda:0', dims=64):
    """
    Calculate the FID score between two datasets using the pytorch_fid command.
    """
    command = f"python -m pytorch_fid {reference_path} {comparison_path} --device {device} --dims {dims}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        output = result.stdout
        # Extract FID score from output
        fid_score = float(output.split()[-1])
        print(f"FID score: {fid_score}")
        return fid_score
    else:
        raise RuntimeError(f"Error calculating FID: {result.stderr}")

def iterate_directories(base_dir, comparison_dirs):
    """
    Iterate through the specified directories to calculate FID scores.
    """
    results = []
    for comp_dir in comparison_dirs:
        if "animations_" in comp_dir:
            for subfolder in ["block", "crouch", "idle", "jump", "receive_crouching_damage", "receive_standing_damage", "run"]:
                reference_subfolder = os.path.join(f"animations_{base_dir.split('_')[0]}" , subfolder)
                comparison_subfolder = os.path.join(comp_dir, subfolder)
                print(f"Calculating FID for {reference_subfolder} and {comparison_subfolder}")
                fid_score = calculate_fid(reference_subfolder, comparison_subfolder)
                results.append((reference_subfolder, comparison_subfolder, fid_score))
        else:
            print(f"Calculating FID for {base_dir} and {comp_dir}")
            fid_score = calculate_fid(base_dir, comp_dir)
            results.append((base_dir, comp_dir, fid_score))
            # Handle subdirectories for animation folders
        
    return results

def write_results_to_csv(results, csv_filename):
    """
    Write the FID scores to a CSV file.
    """
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Reference Dataset', 'Comparison Dataset', 'FID Score'])
        for row in results:
            writer.writerow(row)

def main():
    base_dir = "god_images/"
    comparison_dirs = ["bad_images", "mid_images", "good_images", "animations_bad", "animations_mid", "animations_good"]
    results = iterate_directories(base_dir, comparison_dirs)
    write_results_to_csv(results, "fid_scores.csv")

# Uncomment the following line to run the script
main()

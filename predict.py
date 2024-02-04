import argparse
import os
import time
import torch
from plot.plot import plot_predictions

def get_spec_dir(spect_output_dir):
    '''
    Get the folder most closer to the current time
    to plot the spectrograms
    '''
    now = time.time()
    folders = os.listdir(spect_output_dir)
    get_time = min(folders, key=lambda x: abs(
        now - os.path.getmtime(os.path.join(spect_output_dir, x))))
    return os.path.join(spect_output_dir, get_time)

def prepareToml(data_dir, out_dir):
    '''
    Prepare the toml file for prediction
    - Sets data_dir to the user input
    - Set device to cuda if available else cpu
    - Remove csv_path line if exists
    - Create result directory if not exists
    '''
    # Check cuda availability
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open("predict.toml", "r") as f:
        lines = f.readlines()
        section = "[PREP]"
        for i, line in enumerate(lines):
            # Get the section of the toml file
            if line.startswith("["):
                section = line.strip()
            # Change data_dir section from toml file
            if line.startswith("data_dir"):
                lines[i] = f"data_dir = '{data_dir}'\n"
            if line.startswith("device"):
                lines[i] = f"device = '{device}'\n"
            # Remove csv_path line if exists
            if line.startswith("csv_path"):
                lines.pop(i)
            # Write the output directory
            if line.startswith("output_dir"):
                if section == "[PREP]":
                    dir = os.path.join(out_dir, "data/preprocessed")
                if section == "[PREDICT]":
                    dir = os.path.join(out_dir, "results/predictions")
                lines[i] = f"output_dir = '{dir}'\n"
                os.makedirs(dir)
            if line.startswith("spect_output_dir"):
                dir = os.path.join(out_dir, "data/preprocessed/spec")
                lines[i] = f"spect_output_dir = '{dir}'\n"
                os.makedirs(dir)
            
    # Write the changes to the toml file
    with open("predict.toml", "w") as f:
        f.writelines(lines)

if __name__ == "__main__":
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir",
                        help="Directory containing the data to predict on.",
                        type=str)
    parser.add_argument("out_dir",
                        help="Directory to save the outputs.",
                        type=str)
    parser.add_argument("--plot_spec",
                        help="Plot the spectrograms.",
                        action="store_true")
    args = parser.parse_args()

    data_dir = args.data_dir
    out_dir = args.out_dir
    plot_spec = args.plot_spec

    # Check if data_dir exists
    if not os.path.exists(data_dir):
        raise ValueError(f"{data_dir} does not exist")
    
    # Create directory for output
    # with now hour
    out_dir = os.path.join(out_dir, "outputs_"+time.strftime("%Y%m%d_%H%M%S"))
    os.makedirs(out_dir)

    # Prepare the toml file
    prepareToml(data_dir, out_dir)

    # Run the preprocessing script
    os.system("vak prep predict.toml")
    
    # Run the prediction script
    os.system("vak predict predict.toml")

    if plot_spec:
        with open("predict.toml", "r") as f:
            for line in f:
                # Get the spec directory
                if line.startswith("spect_output_dir"):
                    spect_output_dir = line.split('=')[1].strip().strip('"')
                # Get the output directory
                if line.startswith("output_dir"):
                    output_dir = line.split('=')[1].strip().strip('"')
                # Get the csv file name
                if line.startswith("annot_csv_filename"):
                    csv_name = line.split('=')[1].strip().strip('"')
        annot_csv_path = os.path.join(output_dir, csv_name)

        # Get the spectrogram directory
        spect_dir = get_spec_dir(spect_output_dir)

        # Plot the spectrograms
        # Change the plot_dur, mark_offset, mark_onset if needed
        save_dir = os.path.join(output_dir, "spect_plots")
        os.makedirs(save_dir, exist_ok=True)

        plot_predictions(annot_csv_path, spect_dir,
                         save_dir, plot_dur=10,
                         mark_offset=False, mark_onset=False)

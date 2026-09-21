from rs2.modeler.RS2Modeler import RS2Modeler
from pathlib import Path
import time
import traceback


# -------------------------------------------------------------------
# SETTINGS
# -------------------------------------------------------------------

RS2_PORT = 60054

# Change this to the folder containing your seven RS2 models
MODEL_FOLDER = Path(r"C:\RS2_Temp\Ivrindi\475-yr\New")

# List the files in the exact order in which they should be computed
MODEL_FILES = [
    MODEL_FOLDER / "RSN187-315.fez",
    MODEL_FOLDER / "RSN554-00.fez",
    MODEL_FOLDER / "RSN787-360.fez",
    MODEL_FOLDER / "RSN2893-N.fez",
    MODEL_FOLDER / "RSN3269-E.fez",
    MODEL_FOLDER / "RSN4117-360.fez",
    MODEL_FOLDER / "RSN4894-EW.fez",
]

# Log file recording successful and failed analyses
LOG_FILE = MODEL_FOLDER / "batch_compute_log.txt"


# -------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------

def write_log(message):
    """Write a message to the screen and to the log file."""
    print(message)

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(message + "\n")


def compute_model(modeler, model_path):
    """Open and compute one RS2 model."""
    model = None

    try:
        write_log(f"Opening: {model_path}")

# Open the RS2 model
        model = modeler.openFile(str(model_path))

        write_log(f"Computing: {model_path}")

# This call should return after the model has finished computing
        model.compute()

        write_log(f"COMPLETED: {model_path}")
        return True

    except Exception as error:
        write_log(f"FAILED: {model_path}")
        write_log(f"Error: {error}")
        traceback.print_exc()
        return False

    finally:
        # Close the model before opening the next one
        if model is not None:
            try:
                model.close()
            except Exception as close_error:
                write_log(f"Warning: could not close {model_path}: {close_error}")

# -------------------------------------------------------------------
# MAIN PROGRAM
# -------------------------------------------------------------------

def main():
    # Start RS2 Modeler and its scripting server
    RS2Modeler.startApplication(port=RS2_PORT)

# Connect to the scripting server
    modeler = RS2Modeler(port=RS2_PORT)

# Start a fresh log file
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write("RS2 sequential batch-compute log\n")
        log.write("=" * 50 + "\n")

    successful = 0
    failed = 0

    for index, model_path in enumerate(MODEL_FILES, start=1):

        if not model_path.exists():
            write_log(f"SKIPPED - file not found: {model_path}")
            failed += 1
            continue

        write_log("")
        write_log(f"----- Model {index} of {len(MODEL_FILES)} -----")

        success = compute_model(modeler, model_path)

        if success:
            successful += 1
        else:
            failed += 1

        # Optional short pause between models
        time.sleep(2)

    write_log("")
    write_log("=" * 50)
    write_log(f"Finished. Successful: {successful}; Failed/skipped: {failed}")
    write_log(f"Log file: {LOG_FILE}")

# Close the RS2 Modeler application
    try:
        modeler.close()
    except Exception as error:
        write_log(f"Warning: could not close RS2 Modeler: {error}")


if __name__ == "__main__":
    main()
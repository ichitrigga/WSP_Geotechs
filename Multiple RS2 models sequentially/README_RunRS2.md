# RS2 Sequential Batch Compute

A Python utility that opens and computes a predefined list of RS2 models sequentially through the RS2 Modeler scripting interface. The script records completed, failed, and skipped models in a text log so the batch run can be reviewed afterward.

## What the Script Does

For each model listed in `MODEL_FILES`, the script:

1. Starts RS2 Modeler and its scripting server.
2. Connects to the server through the configured port.
3. Checks whether the model file exists.
4. Opens the model in RS2 Modeler.
5. Runs the model computation.
6. Records the result in `batch_compute_log.txt`.
7. Closes the model before opening the next one.
8. Closes RS2 Modeler after the complete batch is processed.

If one model fails, the script logs the error and continues with the remaining models.

## Requirements

- Windows
- A working RS2 installation
- An RS2 license that permits the required model computations
- Python configured to import the RS2 scripting package
- Access to the `rs2.modeler.RS2Modeler` module

The script uses only standard-library modules in addition to the RS2 scripting package:

- `pathlib`
- `time`
- `traceback`

## Project Files

```text
Run.py
README.md
```

The log file is created automatically in the configured model folder:

```text
batch_compute_log.txt
```

## Configuration

Edit the settings near the top of `Run.py` before running the script.

### 1. RS2 scripting port

```python
RS2_PORT = 60054
```

Use a port available for the RS2 scripting connection.

### 2. Model folder

```python
MODEL_FOLDER = Path(r"C:\RS2_Temp\Ivrindi\475-yr\New")
```

Set this path to the folder containing the RS2 `.fez` model files.

### 3. Model list and computation order

```python
MODEL_FILES = [
    MODEL_FOLDER / "RSN187-315.fez",
    MODEL_FOLDER / "RSN554-00.fez",
    MODEL_FOLDER / "RSN787-360.fez",
    MODEL_FOLDER / "RSN2893-N.fez",
    MODEL_FOLDER / "RSN3269-E.fez",
    MODEL_FOLDER / "RSN4117-360.fez",
    MODEL_FOLDER / "RSN4894-EW.fez",
]
```

Add, remove, rename, or reorder entries as needed. Models are computed from top to bottom in the exact order shown.

### 4. Log-file location

```python
LOG_FILE = MODEL_FOLDER / "batch_compute_log.txt"
```

By default, the log file is saved in the same folder as the models. The file is overwritten at the beginning of each new run.

## How to Run

Open Command Prompt or PowerShell in the folder containing `Run.py`, then run:

```bash
python Run.py
```

Keep the terminal open during execution to view status messages and any errors.

## Example Log Output

```text
RS2 sequential batch-compute log
==================================================

----- Model 1 of 7 -----
Opening: C:\RS2_Temp\Ivrindi\475-yr\New\RSN187-315.fez
Computing: C:\RS2_Temp\Ivrindi\475-yr\New\RSN187-315.fez
COMPLETED: C:\RS2_Temp\Ivrindi\475-yr\New\RSN187-315.fez

==================================================
Finished. Successful: 7; Failed/skipped: 0
Log file: C:\RS2_Temp\Ivrindi\475-yr\New\batch_compute_log.txt
```

## Error Handling

The script handles the following conditions:

- **Missing file:** The model is marked as skipped and the batch continues.
- **Open or compute failure:** The error is logged, the model is closed when possible, and the batch continues.
- **Model close failure:** A warning is logged.
- **RS2 Modeler close failure:** A warning is logged at the end of the run.

A skipped model is included in the final `Failed/skipped` total.

## Important Notes

- Save all model changes before starting the batch.
- Verify the folder path and filenames carefully before running.
- Ensure that the selected port is not being used by another process.
- Avoid manually closing RS2 Modeler while the script is running.
- Review `batch_compute_log.txt` after every run.
- The two-second pause between models is controlled by:

```python
time.sleep(2)
```

Change this value only if a different delay is needed.

## Troubleshooting

### `ModuleNotFoundError: No module named 'rs2'`

The RS2 Python scripting package is not available in the Python environment used to run the script. Use the Python environment configured for the RS2 scripting API or add the RS2 scripting package location to that environment.

### RS2 Modeler does not start or connect

Check that:

- RS2 is installed and licensed.
- `RS2_PORT` is available.
- The RS2 scripting interface is accessible from the selected Python environment.

### A model is skipped

Confirm that:

- The `.fez` file exists in `MODEL_FOLDER`.
- Its filename exactly matches the corresponding entry in `MODEL_FILES`.
- The file extension is correct.

### A model fails during computation

Review both:

- The terminal traceback, which provides detailed Python error information.
- `batch_compute_log.txt`, which identifies the affected model and records the error message.

## License and Use

This repository does not include RS2 or an RS2 license. Users are responsible for complying with the applicable RS2 software license and their organization's requirements for model execution and data handling.

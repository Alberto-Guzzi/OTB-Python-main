# OT Bioelettronica Python Communication Scripts
This project is an adapted version of the original OTB-Python repository developed by OTBioelettronica:
**https://github.com/OTBioelettronica/OTB-Python**

The code has been modified and extended to support the specific requirements of this project while maintaining compatibility with the original OTBioelettronica communication framework.

This repository contains Python scripts for communicating with **OT Bioelettronica** devices. Two implementations are provided, based on different graphical libraries: **PyQt** and **Matplotlib**.

## Repository Structure

### `PyQt/`

This folder contains communication scripts built using the **PyQt** framework.

* Provides a more responsive and optimized graphical interface.
* Better suited for real-time plotting and data acquisition.
* Recommended for practical and experimental use.

#### Accuracy Evaluation

The script used to evaluate the accuracy of a trial is:

```bash
PyQt/otb_accuracy.py
```

To run the script, first activate the OT Bioelettronica Conda environment:

```bash
conda activate OTBioelettronica
```

Then execute:

```bash
python otb_accuracy.py
```
You'll have to select the **.otb4 file** you want to analyze in the window that opens.

The script outputs:

* **Accuracy (%)**: a percentage score representing performance relative to a predefined reference value.
* **RMSE (%)**: the Root Mean Square Error expressed as a percentage, indicating how far the participant's performance deviated from the target trajectory.

---

### `Matplotlib/`

This folder contains an alternative implementation using **Matplotlib**.

While plotting performance is less efficient compared to the PyQt version, it is maintained for completeness and educational purposes.

#### Included Subfolders

##### `device_communication/`

Scripts for establishing and managing communication with OT Bioelettronica devices.

##### `example/`

Example scripts demonstrating how to:

* Send commands to devices
* Receive data streams
* Perform basic input/output operations

---

## Notes

* The **PyQt** implementation is recommended for real-time data acquisition and visualization.
* The **Matplotlib** implementation may be useful for testing, debugging, or environments where PyQt is unavailable.

# NMRS CLIENT VERIFICATION/ TRACKING OUTCOME PROCESSOR

## Project Description
This Python App is used is an Automation Project Resposible for the processing of the Client Tracker and Verification Outcome on the EMR. This Project Reads an Excel File, cleans it up, outputs and maps it to the respective to the EMR.



![Instruction 1](instructions/1_DB_change.png)

![Instruction 2](instructions/2-process_page.png)

![Instruction 3](instructions/3-Process_try_out.png)

![Instruction 4](instructions/4-data_clean.png)

![Instruction 5](instructions/5-download_csv_file.png)

![Instruction 6](instructions/6-Ingest_DATA.png)

![Instruction 7](instructions/7-ingest_tryout.png)

![Instruction 8](instructions/8-ingest-exceute.png)
## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation Guide

### Step 1: Clone the Repository

Clone the project repository from GitHub to your local machine:

```bash
git clone https://github.com/nelson-ust/nmrs_tracking_automator.git
cd nmrs_tracking_automator
```

### Step 2: Set Up a Virtual Environment
Creating a virtual environment is recommended to manage your Python dependencies:

On Windows: 
```bash
python -m venv venv
```
On MacOS and Linux:
```bash
python3 -m venv venv
```

Activate the virtual environment:

On Windows:

```bash
venv\Scripts\activate
```
On macOS and Linux:

```bash
source venv/bin/activate
```
### Step 3: Install Dependencies
Install the required Python packages using pip:

```bash
pip install -r new_requirements.txt
```
### Step 4: Run the Application
Start the FastAPI server using Uvicorn:

```bash
uvicorn api:app --reload
```
### Step 5: Access the Application
Open a web browser and navigate to http://localhost:8000/docs. You should see the Swagger-ui..



## Troubleshooting

If you encounter any issues, ensure you have the correct versions of Python, pip installed, and all the required dependencies also installed using pip.
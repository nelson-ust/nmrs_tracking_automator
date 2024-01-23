# NMRS Client Tracking Automator Project

## Project Description
This NMRS Clienty Tracking Automator Project is designed to Automate the process of completing the Client Tracking Form on the EMR




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

```bash
python -m venv venv
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
pip install -r requirements.txt
```


### Step 5: Run the Application
Run the Data Cleaning Module:

```bash
python /helpers/data_cleaning.py
```

Run the Automation Script:

```bash
python main.py

```
## Troubleshooting

If you encounter any issues, ensure you have the correct versions of Python and pip installed. Also, make sure all environment variables in the .env file are correctly set.

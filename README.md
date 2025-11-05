# Flower count rating tool

This document contains all the information needed to use the Flower Count Rating Tool.

## 1. Python installation

Before using the web application, make sure to set up a Python environment with the required modules.

Check if python is installed: Open your terminal (You can find the terminal as “Command Prompt or Terminal" on Windows) and run (paste and press enter):
```bash
python --version
```

## 2. Python environment setup
if python is installed you will see the version number. If python is not installed, install it from https://www.python.org/downloads/

After installing Python, navigate to your project folder by running:
```bash
cd path/to/your/project
```

Create a virtual environment (commonly named venv):
```bash
python -m venv venv
```

Install required modules (Ensure that the requirements.txt file is located in the same directory as your project):
```bash
pip install -r requirements.txt
```

Activate the virtual environment:
```bash
venv\Scripts\activate
```

## 3. Launch the webapplication
To launch the application, type the following in the terminal (Ensure that the Evaluation_tool.py file is located in the same directory as your project):
```bash
streamlit run Evaluation_tool.py
```
The application will now start and is ready to use.

## 4. Launch via URL

The app is also available via https://flowercountevaluationtool.streamlit.app/
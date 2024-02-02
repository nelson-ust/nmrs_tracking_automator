'''
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Label, Entry, Button, Frame
import requests
import os
import threading

# Function to send POST request to the FastAPI server
def send_post_request(endpoint, file_path, who_attempted=None, progress_callback=None):
    try:
        with open(file_path, 'rb') as file:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            chunk_size = 1024 * 1024  # 1MB chunk size
            
            def file_chunk_generator():
                total_uploaded = 0
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    total_uploaded += len(chunk)
                    if progress_callback:
                        progress_callback(total_uploaded, file_size)
                    yield chunk
            
            file_generator = file_chunk_generator()
            files = {'file': (file_name, file_generator)}
            data = {}

            # Include 'who_attempted' in the data only if it's provided and not empty
            if who_attempted and who_attempted.strip():
                data['who_attempted'] = who_attempted.strip()

            # Send POST request to the FastAPI server
            response = requests.post(f'http://localhost:8000/{endpoint}', files=files, data=data)
            
            if response.status_code == 200:
                messagebox.showinfo('Success', 'File processed successfully')
            else:
                messagebox.showerror('Error', f'Failed to process file: {response.text}')
    except requests.exceptions.ConnectionError:
        messagebox.showerror('Connection Error', 'Failed to connect to the server. Please ensure the FastAPI server is running and accessible.')

# Function to open file dialog and send POST request
def open_file_dialog(endpoint, who_attempted_var=None, progress_bar=None):
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename()
    
    if file_path:
        # Reset the progress bar
        if progress_bar:
            progress_bar['value'] = 0
        
        who_attempted = who_attempted_var.get() if who_attempted_var else None
        
        # Update progress bar in a thread-safe manner
        def update_progress_bar(uploaded, total):
            progress = (uploaded / total) * 100
            if progress_bar:
                progress_bar['value'] = progress
                root.update_idletasks()  # Update the UI
        
        # Run the upload in a separate thread to prevent UI freezing
        threading.Thread(
            target=send_post_request,
            args=(endpoint, file_path, who_attempted),
            kwargs={'progress_callback': update_progress_bar},
            daemon=True
        ).start()
    else:
        messagebox.showwarning('Warning', 'No file selected')

# Create the main window
root = tk.Tk()
root.title('FastAPI Client - Data Ingestion and Processing')

# Set the size of the window
root.geometry('600x400')

# Create main frame to hold everything
main_frame = Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Frame for the process-file form
process_frame = Frame(main_frame, borderwidth=2, relief="groove")
process_frame.pack(fill="both", expand=True, padx=20, pady=10, side=tk.TOP)

# Label for the process-file form
process_label = Label(process_frame, text="Process File Form", font=('Helvetica', 16))
process_label.pack(side=tk.TOP, pady=(0, 10))  # Add some padding to separate from the rest

# Label for who_attempted input in process-file form
who_attempted_label_process = Label(process_frame, text="Who Attempted:")
who_attempted_label_process.pack(side=tk.TOP)

# Text input for who_attempted in process-file form
who_attempted_var_process = tk.StringVar()
who_attempted_entry_process = Entry(process_frame, textvariable=who_attempted_var_process)
who_attempted_entry_process.pack(side=tk.TOP, pady=(0, 10))  # Add some padding to separate from the button

# Button to upload and process data for process-file
process_button = Button(process_frame, text='Upload and Process File', command=lambda: open_file_dialog('process-file', who_attempted_var_process))
process_button.pack(side=tk.TOP)

# Frame for the ingest-data form
ingest_frame = Frame(main_frame, borderwidth=2, relief="groove")
ingest_frame.pack(fill="both", expand=True, padx=20, pady=10, side=tk.BOTTOM)

# Label for the ingest-data form
ingest_label = Label(ingest_frame, text="Ingest Data Form", font=('Helvetica', 16))
ingest_label.pack(side=tk.TOP, pady=(0, 10))  # Add some padding to separate from the button

# Button to upload and process data for ingest-data
ingest_button = Button(ingest_frame, text='Upload and Ingest Data', command=lambda: open_file_dialog('ingest-data'))
ingest_button.pack(side=tk.TOP)

# Progress bar
progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=400, mode='determinate')
progress_bar.pack(side=tk.BOTTOM, pady=(10, 0))

# Run the Tkinter event loop
root.mainloop()

'''

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Label, Entry, Button, Frame
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
import threading
import os

# Function to send POST request to the FastAPI server
def send_post_request(endpoint, file_path, who_attempted=None, progress_callback=None):
    try:
        with open(file_path, 'rb') as file:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            data = {'file': (file_name, file, 'text/plain')}

            # Include 'who_attempted' in the data only if it's provided and not empty
            if who_attempted and who_attempted.strip():
                data['who_attempted'] = who_attempted.strip()

            # Create a multipart encoder and monitor
            encoder = MultipartEncoder(fields=data)
            monitor = MultipartEncoderMonitor(encoder, lambda m: progress_callback(m.bytes_read, file_size))

            # Send POST request to the FastAPI server
            headers = {'Content-Type': monitor.content_type}
            response = requests.post(f'http://localhost:8000/{endpoint}', headers=headers, data=monitor)

            if response.status_code == 200:
                messagebox.showinfo('Success', 'File processed successfully')
            else:
                messagebox.showerror('Error', f'Failed to process file: {response.text}')
    except requests.exceptions.ConnectionError:
        messagebox.showerror('Connection Error', 'Failed to connect to the server. Please ensure the FastAPI server is running and accessible.')

# Function to open file dialog and send POST request
def open_file_dialog(endpoint, who_attempted_var=None, progress_bar=None):
    # Define the file types
    file_types = (
        ('Excel files', '*.xlsx'),
        ('CSV files', '*.csv'),
        ('All files', '*.*')
    )
    
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename(filetypes=file_types)
    
    if file_path:
        # Reset the progress bar
        if progress_bar:
            progress_bar['value'] = 0
        
        who_attempted = who_attempted_var.get() if who_attempted_var else None
        
        # Update progress bar in a thread-safe manner
        def update_progress_bar(uploaded, total):
            progress = (uploaded / total) * 100
            if progress_bar:
                progress_bar['value'] = progress
                root.update_idletasks()  # Update the UI
        
        # Run the upload in a separate thread to prevent UI freezing
        threading.Thread(
            target=send_post_request,
            args=(endpoint, file_path, who_attempted),
            kwargs={'progress_callback': update_progress_bar},
            daemon=True
        ).start()
    else:
        messagebox.showwarning('Warning', 'No file selected')

# Create the main window
root = tk.Tk()
root.title('FastAPI Client - Data Ingestion and Processing')

# Set the size of the window
root.geometry('600x400')

# Create main frame to hold everything
main_frame = Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Frame for the process-file form
process_frame = Frame(main_frame, borderwidth=2, relief="groove")
process_frame.pack(fill="both", expand=True, padx=20, pady=10, side=tk.TOP)

# Label for the process-file form
process_label = Label(process_frame, text="Process File Form", font=('Helvetica', 16))
process_label.pack(side=tk.TOP, pady=(0, 10))  # Add some padding to separate from the rest

# Label for who_attempted input in process-file form
who_attempted_label_process = Label(process_frame, text="Who Attempted:")
who_attempted_label_process.pack(side=tk.TOP)

# Text input for who_attempted in process-file form
who_attempted_var_process = tk.StringVar()
who_attempted_entry_process = Entry(process_frame, textvariable=who_attempted_var_process)
who_attempted_entry_process.pack(side=tk.TOP, pady=(0, 10))  # Add some padding to separate from the button

# Button to upload and process data for process-file
process_button = Button(process_frame, text='Upload and Process File', command=lambda: open_file_dialog('process-file', who_attempted_var_process, progress_bar))
process_button.pack(side=tk.TOP)

# Frame for the ingest-data form
ingest_frame = Frame(main_frame, borderwidth=2, relief="groove")
ingest_frame.pack(fill="both", expand=True, padx=20, pady=10, side=tk.BOTTOM)

# Label for the ingest-data form
ingest_label = Label(ingest_frame, text="Ingest Data Form", font=('Helvetica', 16))
ingest_label.pack(side=tk.TOP, pady=(0, 10))  # Add some padding to separate from the button

# Button to upload and process data for ingest-data
ingest_button = Button(ingest_frame, text='Upload and Ingest Data', command=lambda: open_file_dialog('ingest-data', None, progress_bar))
ingest_button.pack(side=tk.TOP)

# Progress bar
progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=400, mode='determinate')
progress_bar.pack(side=tk.BOTTOM, pady=(10, 0))

# Run the Tkinter event loop
root.mainloop()

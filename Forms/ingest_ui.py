
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Frame, Label, Entry, Button
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
import threading
import os
import time

def send_post_request(endpoint, file_path, who_attempted=None, progress_callback=None, progress_bar=None, root=None):
    try:
        with open(file_path, 'rb') as file:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            data = {'file': (file_name, file, 'text/plain')}

            # Include 'who_attempted' in the data only if it's provided and not empty
            if who_attempted and who_attempted.strip():
                data['who_attempted'] = who_attempted.strip()

            encoder = MultipartEncoder(fields=data)

            # Using lambda function for MultipartEncoderMonitor
            monitor = MultipartEncoderMonitor(encoder, lambda monitor: progress_callback(monitor.bytes_read, file_size) if progress_callback else None)

            headers = {'Content-Type': monitor.content_type}
            response = requests.post(f'http://localhost:8000/{endpoint}', headers=headers, data=monitor)

            if response.status_code == 200:
                messagebox.showinfo('Success', 'File processed successfully')
            else:
                messagebox.showerror('Error', f'Failed to process file: {response.text}')
    except requests.exceptions.ConnectionError:
        messagebox.showerror('Connection Error', 'Failed to connect to the server. Please ensure the FastAPI server is running and accessible.')

def open_file_dialog(endpoint, who_attempted_var=None, progress_bar=None, root=None):
    file_types = (
        ('Excel files', '*.xlsx'),
        ('CSV files', '*.csv'),
        ('All files', '*.*')
    )

    file_path = filedialog.askopenfilename(filetypes=file_types)
    
    if file_path:
        if progress_bar:
            progress_bar['value'] = 0

        who_attempted = who_attempted_var.get() if who_attempted_var else None

        def update_progress_bar(uploaded, total):
            progress = (uploaded / total) * 100
            if progress_bar:
                progress_bar['value'] = progress
                root.update_idletasks()

        threading.Thread(
            target=send_post_request,
            args=(endpoint, file_path, who_attempted),
            kwargs={'progress_callback': update_progress_bar, 'progress_bar': progress_bar, 'root': root},
            daemon=True
        ).start()
    else:
        messagebox.showwarning('Warning', 'No file selected')

root = tk.Tk()
root.title('FastAPI Client - Data Ingestion and Processing')
root.geometry('600x400')

main_frame = Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

process_frame = Frame(main_frame, borderwidth=2, relief="groove")
process_frame.pack(fill="both", expand=True, padx=20, pady=10, side=tk.TOP)

process_label = Label(process_frame, text="Process File Form", font=('Helvetica', 16))
process_label.pack(side=tk.TOP, pady=(0, 10))

who_attempted_label_process = Label(process_frame, text="Who Attempted:")
who_attempted_label_process.pack(side=tk.TOP)

who_attempted_var_process = tk.StringVar()
who_attempted_entry_process = Entry(process_frame, textvariable=who_attempted_var_process)
who_attempted_entry_process.pack(side=tk.TOP, pady=(0, 10))

process_button = Button(process_frame, text='Upload and Process File', command=lambda: open_file_dialog('process-file', who_attempted_var_process, progress_bar, root))
process_button.pack(side=tk.TOP)

ingest_frame = Frame(main_frame, borderwidth=2, relief="groove")
ingest_frame.pack(fill="both", expand=True, padx=20, pady=10, side=tk.BOTTOM)

ingest_label = Label(ingest_frame, text="Ingest Data Form", font=('Helvetica', 16))
ingest_label.pack(side=tk.TOP, pady=(0, 10))

ingest_button = Button(ingest_frame, text='Upload and Ingest Data', command=lambda: open_file_dialog('ingest-data', None, progress_bar, root))
ingest_button.pack(side=tk.TOP)

progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=400, mode='determinate')
progress_bar.pack(side=tk.BOTTOM, pady=(10, 0))

root.mainloop()

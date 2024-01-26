// Function to validate form for data cleanup
function validateForm() {
    // Regular expression for allowed file extensions
    const allowedExtensions = /\.xlsx$/i;

    // Get file input element
    const fileInput = document.getElementById('fileInput');

    // Check if the selected file has a valid extension
    if (!allowedExtensions.test(fileInput.value)) {
        alert('Please select a valid XLSX file.');
        return false;
    }

    // Return true if all validations pass
    return true;
}


// Function to validate form for file ingestion
function ingestForm() {
    const allowedExtensionsCSV = /\.csv$/i;
    const ingestFile = document.getElementById('ingestFile');

    if (!allowedExtensionsCSV.test(ingestFile.value)) {
        alert('Only valid CSV files are allowed.');
        clearFormInputs(ingestFile);
        return false;
    }

    var file = ingestFile.files[0];

    // Create a FormData object
    var formData = new FormData();
    formData.append('file', file);

    // Make a fetch request to the server
    fetch('/ingest-data/', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        // Check if the request was successful
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Return the response
        return response.blob();
    })
    .then(blob => {
        // Create a link element to trigger the download
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = 'processed_file.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });

    // Prevent the form from submitting (you may remove this line if you want the form to submit)
    return false;
}


// Function to clear form inputs
function clearFormInputs(fileInput) {
    fileInput.value = ""; // Clear the file input field
}
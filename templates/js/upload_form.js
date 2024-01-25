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
    // Regular expressions for allowed file extensions and specific file name pattern
    const allowedExtensionsCSV = /\.csv$/i;
    const allowedFileName = /verification_outcome\.csv$/i;

    // Get file input element for ingestion and file path display element
    const ingestFile = document.getElementById('ingestFile');
    const ingestFilePath = document.getElementById('ingestFilePath');

    // Check if the selected file has a valid CSV extension
    if (!allowedExtensionsCSV.test(ingestFile.value)) {
        alert('Only valid CSV files are allowed.');
        clearFormInputs(ingestFile, ingestFilePath);
        return false;
    }

    // Check if the file name follows the specified pattern
    if (!allowedFileName.test(ingestFile.value)) {
        alert('Only file name with verification_outcome is accepted.');
        clearFormInputs(ingestFile, ingestFilePath);
        return false;
    }

    // Display the file path (excluding the full path for security reasons)
    ingestFilePath.value = ingestFile.value;

    console.log(ingestFilePath.value);

    // Return true if all validations pass
    return true;
}

// Function to clear form inputs
function clearFormInputs(fileInput, filePathInput) {
    fileInput.value = ""; // Clear the file input field
    filePathInput.value = ""; // Clear the file path display
}


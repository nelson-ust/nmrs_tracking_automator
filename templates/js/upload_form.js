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
    // Regular expressions for allowed file extensions
    const allowedExtensionsCSV = /\.csv$/i;

    // Get file input element for ingestion
    const ingestFile = document.getElementById('ingestFile');

    // Check if the selected file has a valid CSV extension
    if (!allowedExtensionsCSV.test(ingestFile.value)) {
        alert('Only valid CSV files are allowed.');
        clearFormInputs(ingestFile);
        return false;
    }

    // Read the content of the selected file
    var file = ingestFile.files[0];
    var reader = new FileReader();
    
    reader.onload = function (e) {
        var content = e.target.result;
        console.log(content);
        alert(content);
    };

    // Read the file as text
    reader.readAsText(file);

    // Prevent the form from submitting (you may remove this line if you want the form to submit)
    return false;
}

// Function to clear form inputs
function clearFormInputs(fileInput) {
    fileInput.value = ""; // Clear the file input field
}
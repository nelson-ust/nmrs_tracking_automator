// validate form for data cleanup
function validateForm() {

    var allowedExtensions = /(\.xlsx)$/i;
    var datePattern = /^(\d{2})\/(\d{2})\/(\d{4})$/;
    var fileInput = document.getElementById('fileInput');
    var dateInput = document.getElementById('dateInput');

    if (!fileInput.value.match(allowedExtensions)) {
        alert('Please select a valid XLSX file.');
        return false;
    }

    if (!dateInput.value.match(datePattern)) {
        alert('Please enter a valid date in the format dd/mm/yyyy.');
        return false;
    }

    return true;
}

// validate form for file ingestion
function ingestForm() {
    
    // defining variables
    var allowedExtensionsCSV = /(\.csv)$/i;
    var ingestFile = document.getElementById('ingestFile');
    
    var allowedFileName = /(\verification_outcome.csv)$/i;

    if (!ingestFile.value.match(allowedExtensionsCSV)) {
        alert('only valid CSV files are allowed.');
        ingestFile.value = "";
        return false;
    }

    if (!ingestFile.value.match(allowedFileName)) {
        alert('only file name with verification_outcome is accepted.')
        ingestFile.value = "";;
        return false;
    }

    return true;
}
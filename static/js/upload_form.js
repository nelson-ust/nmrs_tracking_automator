// validate form
        function validateForm() {
            var fileInput = document.getElementById('fileInput');
            var dateInput = document.getElementById('dateInput');
            var allowedExtensions = /(\.xlsx)$/i;
            var datePattern = /^(\d{2})\/(\d{2})\/(\d{4})$/;

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

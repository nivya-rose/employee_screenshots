// upload_validation.js

const nameInput = document.getElementById('name');
const phoneInput = document.getElementById('phone');
const backupInput = document.getElementById('backup_file');
const chatInput = document.getElementById('chat_file');

const backupError = document.getElementById('backup_error');
const backupSuggestion = document.getElementById('backup_suggestion');
const chatError = document.getElementById('chat_error');
const chatSuggestion = document.getElementById('chat_suggestion');

function validateFile(fileInput, type) {
    const name = nameInput.value.trim();
    const phone = phoneInput.value.trim();
    const file = fileInput.files[0];
    if (!file) return true; // no file yet

    const expectedPrefix = `${name}_${phone}_${type}`;
    if (!file.name.startsWith(expectedPrefix)) {
        return { valid: false, suggestion: expectedPrefix + file.name.slice(file.name.lastIndexOf('.')) };
    }
    return { valid: true, suggestion: '' };
}

function updateValidation() {
    let backupResult = validateFile(backupInput, 'backup');
    if (!backupResult.valid) {
        backupError.textContent = 'File name does not match expected format.';
        backupSuggestion.textContent = 'Suggested: ' + backupResult.suggestion;
    } else {
        backupError.textContent = '';
        backupSuggestion.textContent = '';
    }

    let chatResult = validateFile(chatInput, 'chat');
    if (!chatResult.valid) {
        chatError.textContent = 'File name does not match expected format.';
        chatSuggestion.textContent = 'Suggested: ' + chatResult.suggestion;
    } else {
        chatError.textContent = '';
        chatSuggestion.textContent = '';
    }
}

// Real-time validation on file selection or name/phone change
[backupInput, chatInput, nameInput, phoneInput].forEach(el => {
    el.addEventListener('input', updateValidation);
    el.addEventListener('change', updateValidation);
});

// Final check before form submission
document.querySelector('form').addEventListener('submit', e => {
    updateValidation();
    if (backupError.textContent || chatError.textContent) {
        e.preventDefault();
        alert('Please fix file names before submitting.');
    }
});

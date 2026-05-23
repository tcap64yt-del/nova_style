/**
 * Password Show/Hide Toggle Only
 */

document.addEventListener('DOMContentLoaded', () => {

    // Password Visibility Toggle
    const toggleButtons = document.querySelectorAll('.password-toggle');

    toggleButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();

            const input = button.parentElement.querySelector('.form-input');
            const eyeClosed = button.querySelector('.eye-closed');
            const eyeOpen = button.querySelector('.eye-open');

            if (input.type === 'password') {
                input.type = 'text';

                if (eyeClosed) eyeClosed.classList.add('hidden');
                if (eyeOpen) eyeOpen.classList.remove('hidden');

                button.setAttribute('aria-label', 'Hide password');
            } else {
                input.type = 'password';

                if (eyeClosed) eyeClosed.classList.remove('hidden');
                if (eyeOpen) eyeOpen.classList.add('hidden');

                button.setAttribute('aria-label', 'Show password');
            }

            input.focus();
        });
    });

});
const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirmPassword");

// A lowercase letter, a capital letter, a number and length must be between 8 and 24 characters. */
const passwordPattern = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).{8,24}$/;

password.addEventListener("input", checkPasswordDynamic);
confirmPassword.addEventListener("input", checkPasswordDynamic);

function createErrorMsg() {
    const errorContainer = document.createElement("div");
    const errorMsg = `<ul><li>Must include: one lowercase, one capital letter, a number and it must be
    between 8 and 24 characters long.</li></ul>`;

    errorContainer.classList.add("auth_msg", "error");
    errorContainer.insertAdjacentHTML('beforeend', errorMsg);

    return errorContainer;
}

function checkPasswordDynamic(el) {
    const field = el.target;

    if (passwordPattern.test(field.value)) {
        if (field.nextElementSibling) field.nextElementSibling.remove();
    } else {
        if (field.nextElementSibling == null) {
            field.after(createErrorMsg());
            return;
        }
        return;
    }
}
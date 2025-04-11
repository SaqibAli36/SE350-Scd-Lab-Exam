document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerForm");
    const messageElement = document.getElementById("message");

    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        const response = await fetch("http://127.0.0.1:8000/users/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        if (response.ok) {
            messageElement.textContent = "User registered successfully!";
            messageElement.style.color = "green";
        } else {
            messageElement.textContent = data.detail;
            messageElement.style.color = "red";
        }
    });
});

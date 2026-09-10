const API_URL = "http://127.0.0.1:8000";


// =========================
// REGISTER
// =========================

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const username =
            document.getElementById("username").value;

        const passcode =
            document.getElementById("passcode").value;

        const dob =
            document.getElementById("dob").value;

        const message =
            document.getElementById("registerMessage");


        try {

            const response = await fetch(
                `${API_URL}/users/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        username: username,
                        passcode: passcode,
                        dob: dob
                    })
                }
            );


            const data = await response.json();


            if (!response.ok) {

                message.textContent =
                    data.detail || "Registration failed.";

                return;
            }


            message.textContent =
                "Account created successfully. Redirecting...";


            setTimeout(() => {

                window.location.href = "login.html";

            }, 1000);


        } catch (error) {

            console.error(error);

            message.textContent =
                "Unable to connect to DebugPilot.";

        }

    });

}


// =========================
// LOGIN
// =========================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();


        const username =
            document.getElementById("username").value;

        const passcode =
            document.getElementById("passcode").value;

        const message =
            document.getElementById("loginMessage");


        try {

            const response = await fetch(
                `${API_URL}/auth/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        username: username,
                        passcode: passcode
                    })
                }
            );


            const data = await response.json();


            if (!response.ok) {

                message.textContent =
                    data.detail || "Login failed.";

                return;
            }


            // Save JWT
            localStorage.setItem(
                "access_token",
                data.access_token
            );


            message.textContent =
                "Login successful. Redirecting...";


            // Redirect to dashboard
            setTimeout(() => {

                window.location.href = "dashboard.html";

            }, 500);


        } catch (error) {

            console.error(error);

            message.textContent =
                "Unable to connect to DebugPilot.";

        }

    });

}
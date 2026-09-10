const API_URL = "http://127.0.0.1:8000";

const repositorySection =
    document.getElementById("repositorySection");

const loadingSection =
    document.getElementById("loadingSection");

const successSection =
    document.getElementById("successSection");

const failureSection =
    document.getElementById("failureSection");

const repositoryForm =
    document.getElementById("repositoryForm");

const logoutButton =
    document.getElementById("logoutButton");

const openChatButton =
    document.getElementById("openChatButton");

const tryAgainButton =
    document.getElementById("tryAgainButton");

const failureMessage =
    document.getElementById("failureMessage");

const repositoriesList =
    document.getElementById("repositoriesList");

let repositoryId = null;


/* =========================
AUTH CHECK
========================= */

const token =
    localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}


/* =========================
LOGOUT
========================= */

logoutButton.addEventListener(
    "click",
    function () {

        localStorage.removeItem(
            "access_token"
        );

        localStorage.removeItem(
            "repository_id"
        );

        window.location.href =
            "login.html";
    }
);


/* =========================
LOAD USER REPOSITORIES
========================= */

async function loadRepositories() {

    try {

        const response = await fetch(
            `${API_URL}/repositories/`,
            {
                method: "GET",

                headers: {
                    "Authorization":
                        `Bearer ${token}`
                }
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            repositoriesList.innerHTML =
                "<p>Unable to load repositories.</p>";

            console.error(
                "Failed to load repositories:",
                data.detail
            );

            return;
        }


        if (data.length === 0) {

            repositoriesList.innerHTML =
                "<p>No repositories indexed yet.</p>";

            return;
        }


        repositoriesList.innerHTML = "";


        data.forEach((repository) => {

            /* =========================
            REPOSITORY CARD
            ========================= */

            const repositoryCard =
                document.createElement("div");

            repositoryCard.className =
                "repository-item";


            /* =========================
            REPOSITORY INFORMATION
            ========================= */

            const repositoryInfo =
                document.createElement("div");

            repositoryInfo.className =
                "repository-info";


            const repositoryUrl =
                document.createElement("p");

            repositoryUrl.className =
                "repository-url";

            repositoryUrl.textContent =
                repository.repo_url;


            const repositoryStatus =
                document.createElement("span");

            repositoryStatus.className =
                `repository-status ${repository.status}`;

            repositoryStatus.textContent =
                repository.status;


            repositoryInfo.appendChild(
                repositoryUrl
            );

            repositoryInfo.appendChild(
                repositoryStatus
            );


            /* =========================
            OPEN BUTTON
            ========================= */

            const openButton =
                document.createElement("button");

            openButton.className =
                "auth-button repository-open-button";

            openButton.textContent =
                "Open";


            openButton.addEventListener(
                "click",
                function () {

                    localStorage.setItem(
                        "repository_id",
                        repository.id
                    );

                    window.location.href =
                        "chat.html";
                }
            );


            /* =========================
            DELETE BUTTON
            ========================= */

            const deleteButton =
                document.createElement("button");

            deleteButton.className =
                "nav-button repository-delete-button";

            deleteButton.textContent =
                "Delete";


            deleteButton.addEventListener(
                "click",
                async function () {

                    const confirmed =
                        confirm(
                            "Are you sure you want to delete this repository?"
                        );


                    if (!confirmed) {
                        return;
                    }


                    deleteButton.disabled =
                        true;

                    deleteButton.textContent =
                        "Deleting...";


                    try {

                        const response =
                            await fetch(
                                `${API_URL}/repositories/${repository.id}`,
                                {
                                    method: "DELETE",

                                    headers: {
                                        "Authorization":
                                            `Bearer ${token}`
                                    }
                                }
                            );


                        const result =
                            await response.json();


                        if (!response.ok) {

                            throw new Error(
                                result.detail ||
                                "Failed to delete repository."
                            );
                        }


                        /*
                         * Remove repository ID
                         * if it is the currently
                         * selected repository.
                         */

                        if (
                            String(
                                localStorage.getItem(
                                    "repository_id"
                                )
                            ) ===
                            String(repository.id)
                        ) {

                            localStorage.removeItem(
                                "repository_id"
                            );
                        }


                        /*
                         * Reload repository list
                         */

                        await loadRepositories();


                    } catch (error) {

                        console.error(
                            "Delete repository error:",
                            error
                        );


                        alert(
                            error.message ||
                            "Unable to delete repository."
                        );


                        deleteButton.disabled =
                            false;

                        deleteButton.textContent =
                            "Delete";
                    }

                }
            );


            /* =========================
            BUTTON CONTAINER
            ========================= */

            const buttonContainer =
                document.createElement("div");

            buttonContainer.className =
                "repository-actions";


            buttonContainer.appendChild(
                openButton
            );

            buttonContainer.appendChild(
                deleteButton
            );


            /* =========================
            ADD TO CARD
            ========================= */

            repositoryCard.appendChild(
                repositoryInfo
            );

            repositoryCard.appendChild(
                buttonContainer
            );


            repositoriesList.appendChild(
                repositoryCard
            );

        });


    } catch (error) {

        console.error(
            "Repository loading error:",
            error
        );


        repositoriesList.innerHTML =
            "<p>Unable to connect to CodeSense.</p>";
    }
}


loadRepositories();


/* =========================
INGESTION STEPS
========================= */

const steps = [
    "step-cloning",
    "step-parsing",
    "step-chunking",
    "step-embedding",
    "step-storing",
    "step-preparing"
];


function updateStep(index) {

    steps.forEach((stepId, i) => {

        const step =
            document.getElementById(stepId);

        const icon =
            step.querySelector(".step-icon");


        if (i < index) {

            step.classList.remove(
                "active"
            );

            step.classList.add(
                "completed"
            );

            icon.textContent = "✓";

        }

        else if (i === index) {

            step.classList.add(
                "active"
            );

            step.classList.remove(
                "completed"
            );

            icon.textContent = "●";

        }

        else {

            step.classList.remove(
                "active"
            );

            step.classList.remove(
                "completed"
            );

            icon.textContent = "○";
        }

    });
}


/* =========================
SHOW LOADING
========================= */

function startIngestionAnimation() {

    let currentStep = 0;

    updateStep(currentStep);


    const interval =
        setInterval(() => {

            currentStep++;


            if (
                currentStep <
                steps.length
            ) {

                updateStep(
                    currentStep
                );
            }

        }, 2500);


    return interval;
}


/* =========================
ANALYZE REPOSITORY
========================= */

repositoryForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const repoUrl =
            document
                .getElementById("repoUrl")
                .value
                .trim();


        if (!repoUrl) {
            return;
        }


        repositorySection.classList.add(
            "hidden"
        );

        loadingSection.classList.remove(
            "hidden"
        );

        failureSection.classList.add(
            "hidden"
        );

        successSection.classList.add(
            "hidden"
        );


        const animation =
            startIngestionAnimation();


        try {

            const response =
                await fetch(
                    `${API_URL}/repositories/`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Authorization":
                                `Bearer ${token}`
                        },

                        body: JSON.stringify({
                            repo_url: repoUrl
                        })
                    }
                );


            const data =
                await response.json();


            clearInterval(
                animation
            );


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Repository analysis failed."
                );
            }


            /*
             * Backend successfully created
             * and indexed the repository.
             */

            repositoryId =
                data.id;


            localStorage.setItem(
                "repository_id",
                data.id
            );


            /*
             * Complete all UI steps.
             */

            steps.forEach(
                (stepId) => {

                    const step =
                        document.getElementById(
                            stepId
                        );

                    const icon =
                        step.querySelector(
                            ".step-icon"
                        );


                    step.classList.remove(
                        "active"
                    );

                    step.classList.add(
                        "completed"
                    );

                    icon.textContent =
                        "✓";
                }
            );


            /*
             * Small delay so the user
             * can see the completed state.
             */

            setTimeout(
                () => {

                    loadingSection.classList.add(
                        "hidden"
                    );

                    successSection.classList.remove(
                        "hidden"
                    );

                    /*
                     * Refresh repository list
                     * so the newly indexed repo
                     * appears immediately.
                     */

                    loadRepositories();

                },
                700
            );


        } catch (error) {

            clearInterval(
                animation
            );


            console.error(
                "Repository error:",
                error
            );


            loadingSection.classList.add(
                "hidden"
            );

            failureSection.classList.remove(
                "hidden"
            );


            failureMessage.textContent =
                error.message ||
                "Unable to analyze repository.";
        }

    }
);


/* =========================
TRY AGAIN
========================= */

tryAgainButton.addEventListener(
    "click",
    function () {

        failureSection.classList.add(
            "hidden"
        );

        repositorySection.classList.remove(
            "hidden"
        );
    }
);


/* =========================
OPEN CHAT
========================= */

openChatButton.addEventListener(
    "click",
    function () {

        if (!repositoryId) {

            repositoryId =
                localStorage.getItem(
                    "repository_id"
                );
        }


        window.location.href =
            "chat.html";
    }
);
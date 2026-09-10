const API_URL = "http://127.0.0.1:8000";


const token =
    localStorage.getItem("access_token");


const repositoryId =
    localStorage.getItem("repository_id");


const chatForm =
    document.getElementById("chatForm");


const chatInput =
    document.getElementById("chatInput");


const chatMessages =
    document.getElementById("chatMessages");


const sendButton =
    document.getElementById("sendButton");


const logoutButton =
    document.getElementById("logoutButton");


const processingPanel =
    document.getElementById("processingPanel");


const generationTimer =
    document.getElementById("generationTimer");


/* =========================
   AUTH CHECK
========================= */

if (!token || !repositoryId) {

    window.location.href = "login.html";

}


/* =========================
   LOGOUT
========================= */

logoutButton.addEventListener(
    "click",
    function () {

        localStorage.removeItem("access_token");

        localStorage.removeItem("repository_id");

        window.location.href = "login.html";

    }
);


/* =========================
   ADD MESSAGE
========================= */

function addMessage(message, type) {

    const messageElement =
        document.createElement("div");


    messageElement.className =
        `message ${type}-message`;


    const label =
        document.createElement("div");


    label.className =
        "message-label";


    label.textContent =
        type === "user"
            ? "You"
            : "DebugPilot";


    const content =
        document.createElement("p");


    content.textContent = message;


    messageElement.appendChild(label);

    messageElement.appendChild(content);


    chatMessages.appendChild(messageElement);


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    return messageElement;
}

/* =========================
LOAD CHAT HISTORY
========================= */

async function loadChatHistory() {
    try {
        const response = await fetch(
            `${API_URL}/chat/${repositoryId}`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            console.error(
                "Failed to load chat history:",
                data.detail
            );
            return;
        }

        data.forEach((chat) => {
            addMessage(chat.query, "user");
            addMessage(chat.answer, "assistant");
        });

    } catch (error) {
        console.error(
            "Chat history error:",
            error
        );
    }
}


/* =========================
   RAG STEPS
========================= */

const ragSteps = [
    "rag-retrieving",
    "rag-reranking",
    "rag-context",
    "rag-generating"
];


function resetRagSteps() {

    ragSteps.forEach((stepId) => {

        const step =
            document.getElementById(stepId);


        const icon =
            step.querySelector(".rag-icon");


        step.classList.remove("active");

        step.classList.remove("completed");

        icon.textContent = "○";

    });

}


function updateRagStep(index) {

    ragSteps.forEach((stepId, i) => {

        const step =
            document.getElementById(stepId);


        const icon =
            step.querySelector(".rag-icon");


        if (i < index) {

            step.classList.remove("active");

            step.classList.add("completed");

            icon.textContent = "✓";

        }

        else if (i === index) {

            step.classList.add("active");

            step.classList.remove("completed");

            icon.textContent = "●";

        }

        else {

            step.classList.remove("active");

            step.classList.remove("completed");

            icon.textContent = "○";

        }

    });

}


/* =========================
   RAG PROCESSING ANIMATION
========================= */

function startRagProcessing() {

    resetRagSteps();


    processingPanel.classList.remove("hidden");


    let currentStep = 0;


    updateRagStep(currentStep);


    /*
     * Move through the RAG stages visually.
     *
     * This is a frontend progress animation.
     * The actual answer still comes from the backend.
     */

    const stepInterval = setInterval(() => {

        currentStep++;


        if (currentStep < ragSteps.length) {

            updateRagStep(currentStep);

        }

    }, 1800);


    return stepInterval;
}


/* =========================
   TIMER
========================= */

function startTimer() {

    const startTime =
        performance.now();


    generationTimer.textContent =
        "0.0s";


    const timerInterval =
        setInterval(() => {

            const elapsed =
                (performance.now() - startTime) / 1000;


            generationTimer.textContent =
                `${elapsed.toFixed(1)}s`;

        }, 100);


    return {
        timerInterval,
        startTime
    };
}


/* =========================
   COMPLETE RAG STEPS
========================= */

function completeRagSteps() {

    ragSteps.forEach((stepId) => {

        const step =
            document.getElementById(stepId);


        const icon =
            step.querySelector(".rag-icon");


        step.classList.remove("active");

        step.classList.add("completed");

        icon.textContent = "✓";

    });

}


/* =========================
   SEND CHAT
========================= */

chatForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const query =
            chatInput.value.trim();


        if (!query) {
            return;
        }


        /*
         * Show user question.
         */

        addMessage(
            query,
            "user"
        );


        chatInput.value = "";


        /*
         * Disable input while
         * RAG is running.
         */

        chatInput.disabled = true;

        sendButton.disabled = true;

        sendButton.textContent =
            "Analyzing...";


        /*
         * Start RAG visual flow.
         */

        const ragInterval =
            startRagProcessing();


        /*
         * Start generation timer.
         */

        const timer =
            startTimer();


        try {

            const response = await fetch(
                `${API_URL}/chat/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${token}`
                    },

                    body: JSON.stringify({

                        repository_id:
                            Number(repositoryId),

                        query: query

                    })
                }
            );


            const data =
                await response.json();


            /*
             * Backend finished.
             */

            clearInterval(ragInterval);

            clearInterval(timer.timerInterval);


            /*
             * Show final elapsed time.
             */

            const finalTime =
                (
                    (performance.now() -
                        timer.startTime) / 1000
                ).toFixed(1);


            generationTimer.textContent =
                `${finalTime}s`;


            /*
             * Complete all RAG stages.
             */

            completeRagSteps();


            if (!response.ok) {

                processingPanel.classList.add(
                    "hidden"
                );


                addMessage(
                    data.detail ||
                    "Something went wrong while processing your question.",
                    "assistant"
                );


                return;
            }


            /*
             * Small delay so the user
             * can see all steps completed.
             */

            setTimeout(() => {

                processingPanel.classList.add(
                    "hidden"
                );


                addMessage(
                    data.answer,
                    "assistant"
                );


            }, 500);


        }

        catch (error) {

            console.error(
                "Chat error:",
                error
            );


            clearInterval(ragInterval);

            clearInterval(timer.timerInterval);


            processingPanel.classList.add(
                "hidden"
            );


            addMessage(
                "Unable to connect to DebugPilot.",
                "assistant"
            );

        }

        finally {

            /*
             * Re-enable input after
             * the backend request finishes.
             */

            setTimeout(() => {

                chatInput.disabled = false;

                sendButton.disabled = false;

                sendButton.textContent =
                    "Send";

                chatInput.focus();

            }, 600);

        }

    }
);

loadChatHistory();
function getVisitorId() {
    let visitorId = localStorage.getItem("visitor_id");

    if (!visitorId) {
        visitorId = crypto.randomUUID();
        localStorage.setItem("visitor_id", visitorId);
    }

    return visitorId;
}


// =========================
// CLICK TRACKING
// =========================

async function loadUserClicks() {

    const userCounter =
        document.getElementById("user-clicks");

    if (!userCounter) {
        return;
    }

    try {

        const visitorId = getVisitorId();

        const response = await fetch(
            `/api/clicks?visitor_id=${encodeURIComponent(visitorId)}`
        );

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        userCounter.textContent = data.user_clicks;

    } catch (error) {

        console.error(
            "Failed to load click count:",
            error
        );

    }
}


const clickButton =
    document.getElementById("click-button");

if (clickButton) {

    clickButton.addEventListener("click", async () => {

        try {

            const response = await fetch("/api/click", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    visitor_id: getVisitorId()
                })
            });

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            const globalCounter =
                document.getElementById("global-clicks");

            const userCounter =
                document.getElementById("user-clicks");

            if (globalCounter) {
                globalCounter.textContent = data.clicks;
            }

            if (userCounter) {
                userCounter.textContent = data.user_clicks;
            }

        } catch (error) {

            console.error(
                "Failed to record click:",
                error
            );

        }

    });
}


loadUserClicks();

// =========================
// TIME TRACKING
// =========================

let activeStartTime = null;
let accumulatedTime = 0;
let displayedTime = 0;

const TIME_INTERVAL = 30;


// =========================
// TIME DISPLAY
// =========================

function formatTime(seconds) {

    const hours = Math.floor(seconds / 3600);

    const minutes =
        Math.floor((seconds % 3600) / 60);

    const remainingSeconds =
        seconds % 60;

    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
}


function updateTimeDisplay() {

    const timeCounter =
        document.getElementById("user-time");

    if (!timeCounter) {
        return;
    }

    timeCounter.textContent =
        formatTime(displayedTime);

}


// =========================
// LOAD EXISTING TIME
// =========================

async function loadUserTime() {

    const timeCounter =
        document.getElementById("user-time");

    if (!timeCounter) {
        return;
    }

    try {

        const visitorId = getVisitorId();

        const response = await fetch(
            `/api/time?visitor_id=${encodeURIComponent(visitorId)}`
        );

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        displayedTime = data.user_time || 0;

        updateTimeDisplay();

    } catch (error) {

        console.error(
            "Failed to load user time:",
            error
        );

    }

}


loadUserTime();


// =========================
// TIMER
// =========================

function startTimeTracking() {

    if (activeStartTime === null) {
        activeStartTime = Date.now();
    }

}


function stopTimeTracking() {

    if (activeStartTime === null) {
        return;
    }

    const elapsedSeconds =
        Math.floor(
            (Date.now() - activeStartTime) / 1000
        );

    accumulatedTime += elapsedSeconds;

    activeStartTime = null;

}


// =========================
// SEND TIME TO BACKEND
// =========================

async function sendTime(durationSeconds) {

    if (durationSeconds <= 0) {
        return;
    }

    try {

        const response = await fetch("/api/time", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                visitor_id: getVisitorId(),
                duration_seconds: durationSeconds
            })
        });

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        // Sync with the value stored in Supabase.
        displayedTime = data.user_time;

        updateTimeDisplay();

    } catch (error) {

        console.error(
            "Failed to record time:",
            error
        );

    }

}


// =========================
// LIVE STOPWATCH
// =========================

setInterval(() => {

    if (document.visibilityState !== "visible") {
        return;
    }

    if (activeStartTime === null) {
        return;
    }

    displayedTime++;

    updateTimeDisplay();

}, 1000);


// =========================
// SAVE EVERY 30 SECONDS
// =========================

setInterval(
    async () => {

        if (document.visibilityState !== "visible") {
            return;
        }

        stopTimeTracking();

        if (accumulatedTime <= 0) {
            startTimeTracking();
            return;
        }

        const timeToSend =
            accumulatedTime;

        accumulatedTime = 0;

        await sendTime(timeToSend);

        startTimeTracking();

    },
    TIME_INTERVAL * 1000
);


// =========================
// VISIBILITY
// =========================

document.addEventListener(
    "visibilitychange",
    () => {

        if (document.visibilityState === "hidden") {

            stopTimeTracking();

        } else {

            startTimeTracking();

        }

    }
);


// =========================
// SAVE WHEN LEAVING
// =========================

window.addEventListener(
    "beforeunload",
    () => {

        stopTimeTracking();

        if (accumulatedTime <= 0) {
            return;
        }

        const data = JSON.stringify({
            visitor_id: getVisitorId(),
            duration_seconds: accumulatedTime
        });

        navigator.sendBeacon(
            "/api/time",
            new Blob(
                [data],
                {
                    type: "application/json"
                }
            )
        );

        accumulatedTime = 0;

    }
);


// Start tracking.
if (document.visibilityState === "visible") {
    startTimeTracking();
}
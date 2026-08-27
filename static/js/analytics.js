function getVisitorId() {
    let visitorId = localStorage.getItem("visitor_id");

    if (!visitorId) {
        visitorId = crypto.randomUUID();
        localStorage.setItem("visitor_id", visitorId);
    }

    return visitorId;
}


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
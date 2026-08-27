function getVisitorId() {
    let visitorId = localStorage.getItem("visitor_id");

    if (!visitorId) {
        visitorId = crypto.randomUUID();
        localStorage.setItem("visitor_id", visitorId);
    }

    return visitorId;
}
const clickButton = document.getElementById("click-button");

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

            const counter = document.querySelector(".counter-number");

            if (counter) {
                counter.textContent = data.clicks;
            }
        } catch (error) {
            console.error("Failed to record click:", error);
        }
    });
}
// =========================
// LOCATION MAP
// =========================

const locationMapElement =
    document.getElementById("location-map");


if (locationMapElement) {

    fetch(
        "https://tiles.openfreemap.org/styles/dark"
    )
        .then(response => {

            if (!response.ok) {
                throw new Error(
                    "Failed to load map style"
                );
            }

            return response.json();

        })
        .then(style => {

            const map =
                new maplibregl.Map({

                    container: "location-map",

                    style: style,

                    // Bangalore
                    center: [
                        77.5946,
                        12.9716
                    ],

                    zoom: 11.5,

                    minZoom: 9,

                    maxZoom: 17,

                    attributionControl: true

                });


            // Zoom controls

            map.addControl(
                new maplibregl.NavigationControl({
                    showCompass: false
                }),
                "top-right"
            );

        })
        .catch(error => {

            console.error(
                "Failed to initialize location map:",
                error
            );

        });

}


// =========================
// BANGALORE TIME
// =========================

const bangaloreTime =
    document.getElementById("bangalore-time");


function updateBangaloreTime() {

    if (!bangaloreTime) {
        return;
    }


    const now = new Date();


    const time =
        new Intl.DateTimeFormat(
            "en-IN",
            {
                timeZone: "Asia/Kolkata",

                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",

                hour12: false
            }
        ).format(now);


    bangaloreTime.textContent = time;
}


updateBangaloreTime();


setInterval(
    updateBangaloreTime,
    1000
);
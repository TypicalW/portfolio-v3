// =========================
// UNIFIED CONTEST HISTORY
// =========================

async function loadContestHistory() {

    const contestList =
        document.getElementById("contest-history");

    if (!contestList) {
        return;
    }


    try {

        const response =
            await fetch("/api/contests");


        if (!response.ok) {
            return;
        }


        const data =
            await response.json();


        if (!data.contests) {
            return;
        }


        contestList.innerHTML = "";


        data.contests.forEach(contest => {

            const row =
                document.createElement("div");

            row.className = "contest-row";


            // =========================
            // CONTEST NAME
            // =========================

            const name =
                document.createElement("span");

            name.textContent =
                contest.contest;


            // =========================
            // RATING
            // =========================

            const rating =
                document.createElement("span");

            rating.textContent =
                contest.rating_after_contest;


            // =========================
            // DATE
            // =========================

            const date =
                document.createElement("span");


            const contestDate =
                new Date(contest.date);


            date.textContent =
                contestDate.toLocaleDateString(
                    "en-US",
                    {
                        month: "short",
                        day: "numeric",
                        year: "numeric"
                    }
                );


            // =========================
            // ADD ROW
            // =========================

            row.appendChild(name);

            row.appendChild(rating);

            row.appendChild(date);


            contestList.appendChild(row);

        });


    } catch (error) {

        console.error(
            "Failed to load contest history:",
            error
        );

    }

}


loadContestHistory();
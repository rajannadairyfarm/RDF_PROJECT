document.addEventListener("DOMContentLoaded", function () {

    const fields = [
        {
            id: "id_seo_title",
            max: 60
        },
        {
            id: "id_seo_description",
            max: 160
        }
    ];

    fields.forEach(function (config) {

        const field = document.getElementById(config.id);

        if (!field) {
            return;
        }

        const counter = document.createElement("div");

        counter.className = "rdf-seo-counter";

        counter.style.marginTop = "6px";
        counter.style.fontSize = "13px";

        field.parentNode.appendChild(counter);

        function updateCounter() {

            const length = field.value.length;

            counter.textContent =
                `${length} / ${config.max} characters`;

            if (length === 0) {
                counter.textContent +=
                    " — Recommended";
            }
            else if (length <= config.max) {
                counter.textContent +=
                    " — Good length";
            }
            else {
                counter.textContent +=
                    " — Too long";
            }
        }

        field.addEventListener(
            "input",
            updateCounter
        );

        updateCounter();
    });
});
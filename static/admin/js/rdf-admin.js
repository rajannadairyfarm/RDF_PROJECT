document.addEventListener("DOMContentLoaded", function () {

    const toggles = document.querySelectorAll(
        ".rdf-sidebar-group-toggle"
    );


    toggles.forEach(function (toggle) {

        const targetId = toggle.dataset.target;

        const group = document.getElementById(
            targetId
        );


        if (!group) {
            return;
        }


        /*
         * If this section contains the active page,
         * always keep it expanded.
         */

        const activeLink = group.querySelector(
            ".rdf-sidebar-link.active"
        );


        if (activeLink) {

            group.classList.remove(
                "collapsed"
            );

            toggle.classList.remove(
                "collapsed"
            );

        }


        toggle.addEventListener(
            "click",
            function () {

                const isCollapsed =
                    group.classList.toggle(
                        "collapsed"
                    );

                toggle.classList.toggle(
                    "collapsed",
                    isCollapsed
                );

            }
        );

    });

});
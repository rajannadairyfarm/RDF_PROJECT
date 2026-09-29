document.addEventListener("DOMContentLoaded", function () {

    const imageInput = document.getElementById("profile-image");
    const preview = document.getElementById("profilePreview");
    const placeholder = document.getElementById("profilePlaceholder");

    if (!imageInput) {
        return;
    }

    imageInput.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) {
            return;
        }

        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];

        const maxSize = 5 * 1024 * 1024;

        if (!allowedTypes.includes(file.type)) {

            alert(
                "Only JPG, PNG, and WebP images are allowed."
            );

            this.value = "";

            return;
        }

        if (file.size > maxSize) {

            alert(
                "Profile image must be smaller than 5 MB."
            );

            this.value = "";

            return;
        }

        const reader = new FileReader();

        reader.onload = function (event) {

            if (preview) {

                preview.src = event.target.result;

            } else {

                const image = document.createElement("img");

                image.src = event.target.result;
                image.id = "profilePreview";
                image.alt = "Profile preview";

                if (placeholder) {
                    placeholder.replaceWith(image);
                }

            }

        };

        reader.readAsDataURL(file);

    });

});
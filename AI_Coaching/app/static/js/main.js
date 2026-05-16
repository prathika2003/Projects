document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll(".validate-form");
    const animatedItems = document.querySelectorAll(
        ".dashboard-head, .auth-panel, .narrow, .panel, .form-card, .question-card, .flash"
    );

    animatedItems.forEach((item, index) => {
        item.classList.add("reveal-on-scroll");
        item.style.setProperty("--reveal-delay", `${Math.min(index * 45, 220)}ms`);
    });

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.14, rootMargin: "0px 0px -40px 0px" }
        );

        animatedItems.forEach((item) => observer.observe(item));
    } else {
        animatedItems.forEach((item) => item.classList.add("is-visible"));
    }

    forms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            let valid = true;
            form.querySelectorAll(".validation-message").forEach((message) => message.remove());
            form.querySelectorAll(".field-error").forEach((field) => field.classList.remove("field-error"));

            form.querySelectorAll("input, select, textarea").forEach((field) => {
                if (!field.checkValidity()) {
                    valid = false;
                    field.classList.add("field-error");
                    const message = document.createElement("p");
                    message.className = "validation-message";
                    message.textContent = field.validationMessage || "Please complete this field.";
                    field.insertAdjacentElement("afterend", message);
                }
            });

            if (!valid) {
                event.preventDefault();
            }
        });
    });
});

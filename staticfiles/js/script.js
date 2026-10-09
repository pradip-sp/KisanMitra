document.addEventListener("DOMContentLoaded", function () {
    document.documentElement.style.scrollBehavior = "smooth";

    const body = document.body;
    const menuBtn = document.querySelector(".menu-btn");
    const navLinks = document.querySelector(".nav-links");
    const themeToggle = document.querySelector(".theme-toggle");
    const progressBar = document.getElementById("progress-bar");
    const topBtn = document.getElementById("topBtn");
    // const newsletterButton = document.querySelector(".newsletter button");
    // const newsletterInput = document.querySelector(".newsletter input");
    const animatingCards = document.querySelectorAll(".card, .blog-post");
    const currentPage = window.location.pathname.split("/").pop() || "index.html";

    function updateProgressBar() {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        if (progressBar) {
            progressBar.style.width = progress + "%";
        }

        if (topBtn) {
            topBtn.style.display = scrollTop > 300 ? "block" : "none";
        }
    }

    function setTheme(isDark) {
        body.classList.toggle("dark", isDark);

        if (themeToggle) {
            themeToggle.textContent = isDark ? "☀️" : "🌙";
            themeToggle.setAttribute("aria-label", isDark ? "Switch to light theme" : "Switch to dark theme");
        }

        try {
            localStorage.setItem("nova-theme", isDark ? "dark" : "light");
        } catch (error) {
            // Ignore storage failures in restricted environments.
        }
    }

    function revealCard(card) {
        card.style.opacity = "1";
    }

    if (menuBtn && navLinks) {
        menuBtn.addEventListener("click", function () {
            const isOpen = navLinks.style.display === "flex";
            navLinks.style.display = isOpen ? "none" : "flex";
        });

        navLinks.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                if (window.innerWidth <= 900) {
                    navLinks.style.display = "none";
                }
            });
        });

        window.addEventListener("resize", function () {
            if (window.innerWidth > 900) {
                navLinks.style.display = "";
            }
        });
    }

    if (themeToggle) {
        let storedTheme = null;

        try {
            storedTheme = localStorage.getItem("nova-theme");
        } catch (error) {
            storedTheme = null;
        }

        setTheme(storedTheme === "dark");

        themeToggle.addEventListener("click", function () {
            setTheme(!body.classList.contains("dark"));
        });
    }

    if (topBtn) {
        topBtn.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // if (newsletterButton && newsletterInput) {
    //     newsletterButton.addEventListener("click", function () {
    //         const email = newsletterInput.value.trim();

    //         if (!email) {
    //             alert("Please enter your email address.");
    //             newsletterInput.focus();
    //             return;
    //         }

    //         alert("Subscribed Successfully!");
    //         newsletterInput.value = "";
    //     });
    // }


    animatingCards.forEach(function (card) {
        card.style.opacity = "0";
    });

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(function (entries, observerInstance) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    revealCard(entry.target);
                    observerInstance.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.15,
        });

        animatingCards.forEach(function (card) {
            observer.observe(card);
        });
    } else {
        animatingCards.forEach(function (card) {
            revealCard(card);
        });
    }

    // maine add kiya hai 

    document.addEventListener("DOMContentLoaded", function () {

        const currentPage = window.location.pathname.split("/").pop() || "index.html";

        document.querySelectorAll("nav a").forEach(function (link) {

            const linkPage = link.getAttribute("href").split("/").pop();

            if (linkPage === currentPage) {
                link.classList.add("active");
            }

        });

    });
    updateProgressBar();
    window.addEventListener("scroll", updateProgressBar, { passive: true });
});
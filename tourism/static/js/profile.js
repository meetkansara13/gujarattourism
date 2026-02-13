// ------------------------- TAB SWITCHING -------------------------
const tabs = document.querySelectorAll(".tab-btn");
const contents = document.querySelectorAll(".tab-content");

tabs.forEach(btn => {
    btn.addEventListener("click", () => {
        tabs.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        contents.forEach(c => c.classList.remove("active"));
        document.getElementById(btn.dataset.tab).classList.add("active");
    });
});

// ------------------------- DARK MODE -------------------------
const themeSwitch = document.getElementById("themeSwitch");
const body = document.body;

if (localStorage.getItem("theme") === "dark") {
    body.classList.replace("light", "dark");
    themeSwitch.checked = true;
}

themeSwitch.addEventListener("change", () => {
    if (themeSwitch.checked) {
        body.classList.replace("light", "dark");
        localStorage.setItem("theme", "dark");
    } else {
        body.classList.replace("dark", "light");
        localStorage.setItem("theme", "light");
    }
});

// ------------------------- LOGOUT -------------------------
document.querySelector(".logout-btn").addEventListener("click", () => {
    if (confirm("Are you sure you want to logout?")) {
        window.location.href = "/logout/";
    }
});

// ------------------------- PROFILE IMAGE UPLOAD PREVIEW -------------------------
const imageInput = document.getElementById("profileImageUpload");
const imgElement = document.querySelector(".profile-img");

imageInput?.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        imgElement.src = URL.createObjectURL(file);
        this.closest("form").submit();
    }
});

// ------------------------- FILTER & SORT BOOKINGS -------------------------
const filterStatus = document.getElementById("filterStatus");
const sortSelect = document.getElementById("sortBookings");
const bookingList = document.getElementById("bookingList");

function applyFilters() {
    const statusValue = filterStatus.value;

    document.querySelectorAll(".booking-card").forEach(card => {
        const status = card.dataset.status;
        card.style.display =
            statusValue === "all" || status === statusValue
                ? "flex"
                : "none";
    });
}

function sortBookings() {
    const value = sortSelect.value;

    const cards = [...document.querySelectorAll(".booking-card")];
    cards.sort((a, b) => {
        const dateA = new Date(a.dataset.date);
        const dateB = new Date(b.dataset.date);
        return value === "new" ? dateB - dateA : dateA - dateB;
    });

    bookingList.innerHTML = "";
    cards.forEach(card => bookingList.appendChild(card));
}

filterStatus?.addEventListener("change", applyFilters);
sortSelect?.addEventListener("change", sortBookings);

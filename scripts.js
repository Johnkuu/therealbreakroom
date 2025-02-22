document.addEventListener("DOMContentLoaded", () => {
    const profileContainer = document.getElementById("profile-container");
    const chooseProfileContainer = document.getElementById("choose-profile-container");
    const createProfileContainer = document.getElementById("create-profile-container");

    const createProfileButton = document.querySelector(".create-profile-button");
    const backButtons = document.querySelectorAll(".back-button");
    const createProfileForm = document.getElementById("create-profile-form");
    const startButton = document.querySelector(".start-button");

    const predefinedProfiles = [
        { name: "John", avatar: "avatar_1.png", deletable: false },
        { name: "Maria", avatar: "avatar_2.png", deletable: false },
    ];

    let createdProfiles = JSON.parse(localStorage.getItem("createdProfiles")) || [];

    // Initial Render of Profiles
    renderProfileList();

    // Expand Create Profile Section
    createProfileButton.addEventListener("click", () => {
        createProfileContainer.classList.toggle("hidden");
    });

    // Handle navigation back to Profiles
    backButtons.forEach(button => {
        button.addEventListener("click", () => {
            showContainer(chooseProfileContainer);
        });
    });

    // Handle profile selection
    chooseProfileContainer.addEventListener("click", (e) => {
        if (e.target.closest(".profile-option")) {
            const button = e.target.closest(".profile-option");
            const name = button.getAttribute("data-name");
            const avatar = button.getAttribute("data-avatar");
            displayProfile({ name, avatar });
        }
    });

    // Handle new profile creation
    createProfileForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const nameInput = document.getElementById("name");
        const avatarInput = document.getElementById("avatar");

        if (!nameInput.value || !avatarInput.files[0]) {
            alert("Please provide both a name and an avatar.");
            return;
        }

        // Check if name is already taken
        const allProfiles = [...predefinedProfiles, ...createdProfiles];
        if (allProfiles.some(profile => profile.name.toLowerCase() === nameInput.value.toLowerCase())) {
            alert("This name is already in use. Please choose a different name.");
            return;
        }

        const reader = new FileReader();
        reader.onload = function (event) {
            const profile = {
                name: nameInput.value,
                avatar: event.target.result,
                deletable: true,
            };

            createdProfiles.push(profile);
            localStorage.setItem("createdProfiles", JSON.stringify(createdProfiles));
            renderProfileList();
            displayProfile(profile);
        };

        reader.readAsDataURL(avatarInput.files[0]);
    });

    // Handle Start button navigation
    startButton.addEventListener("click", () => {
        window.location.href = "index.html";
    });

    // Render Profile List
    function renderProfileList() {
        const profileListContainer = document.querySelector(".predefined-profiles");
        profileListContainer.innerHTML = "";

        const allProfiles = [...predefinedProfiles, ...createdProfiles];

        allProfiles.forEach(profile => {
            const profileElement = document.createElement("div");
            profileElement.classList.add("profile-option");

            profileElement.setAttribute("data-name", profile.name);
            profileElement.setAttribute("data-avatar", profile.avatar);

            profileElement.innerHTML = `
                <img src="${profile.avatar}" alt="${profile.name}'s Avatar" class="profile-avatar">
                <span>${profile.name}</span>
                ${profile.deletable ? '<button class="delete-button">Delete</button>' : ""}`;
                
            if (profile.deletable) {
                profileElement.querySelector(".delete-button").addEventListener("click", (e) => {
                    e.stopPropagation();
                    const confirmDelete = confirm(`Are you sure you want to delete the profile "${profile.name}"?`);
                    if (confirmDelete) {
                        createdProfiles = createdProfiles.filter(p => p.name !== profile.name);
                        localStorage.setItem("createdProfiles", JSON.stringify(createdProfiles));
                        renderProfileList();
                    }
                });
            }

            profileListContainer.appendChild(profileElement);
        });
    }

    // Display Selected Profile
    function displayProfile(profile) {
        profileContainer.querySelector(".profile-image").src = profile.avatar;
        profileContainer.querySelector(".profile-name").textContent = `Welcome, ${profile.name}!`;
        showContainer(profileContainer);
    }

    function showContainer(containerToShow) {
        profileContainer.classList.add("hidden");
        chooseProfileContainer.classList.add("hidden");
        createProfileContainer.classList.add("hidden");
        containerToShow.classList.remove("hidden");
    }
});

const responseBox = document.querySelector("#response-box");
const profileBox = document.querySelector("#profile-box");
const apiUrl = document.querySelector("#api-url");
const registerForm = document.querySelector("#register-form");
const loginForm = document.querySelector("#login-form");
const profileButton = document.querySelector("#profile-button");
const logoutButton = document.querySelector("#logout-button");

let token = localStorage.getItem("api-login-token");

apiUrl.textContent = window.location.origin;

function showResponse(data) {
    responseBox.textContent = JSON.stringify(data, null, 2);
}

function getFormData(form) {
    return Object.fromEntries(new FormData(form).entries());
}

async function requestJson(path, options = {}) {
    const response = await fetch(path, options);
    const data = await response.json();

    if (!response.ok) {
        throw data;
    }

    return data;
}

function renderProfile(user) {
    profileBox.innerHTML = `
        <dl>
            <dt>ID</dt>
            <dd>${user.id}</dd>
            <dt>Nome</dt>
            <dd>${user.name}</dd>
            <dt>Email</dt>
            <dd>${user.email}</dd>
        </dl>
    `;
}

function clearProfile() {
    profileBox.innerHTML = '<span class="empty-state">Faca login para carregar o perfil.</span>';
}

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        const data = await requestJson("/cadastro", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(getFormData(registerForm)),
        });
        showResponse(data);
    } catch (error) {
        showResponse(error);
    }
});

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        const data = await requestJson("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(getFormData(loginForm)),
        });
        token = data.token;
        localStorage.setItem("api-login-token", token);
        renderProfile(data.usuario);
        showResponse(data);
    } catch (error) {
        showResponse(error);
    }
});

profileButton.addEventListener("click", async () => {
    try {
        const data = await requestJson("/perfil", {
            headers: { Authorization: `Bearer ${token}` },
        });
        renderProfile(data.usuario);
        showResponse(data);
    } catch (error) {
        showResponse(error);
    }
});

logoutButton.addEventListener("click", async () => {
    try {
        const data = await requestJson("/logout", {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
        });
        token = null;
        localStorage.removeItem("api-login-token");
        clearProfile();
        showResponse(data);
    } catch (error) {
        showResponse(error);
    }
});

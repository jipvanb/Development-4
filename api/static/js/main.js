
function register(e) {
    // Check if passwords match
    if (getValue("password1") != getValue("confirm")) {
        console.warn("Passwords do not match");
        return;
    }

    // Fetch data from html
    let data = {
        password: getValue("password1"),
        email: getValue("email1"),
        first_name: getValue("firstname"),
        last_name: getValue("lastname"),
        phonenumber: getValue("phonenumber")

    };

    // Submit data to API
    // api("users", "POST", data).then((res) => {
    //     if (res.message == 'success') {
    //         alert("User created successfully");
    //     }
    // });
}

function login() {
    // Fetch data from html
    let data = {
        email: getValue("email2"),
        password: getValue("password2"),
    };

    // Submit data to API
    api("auth", "POST", data).then((res) => {
        if (res.message == 'success') {
            setCookie("token", res.access_token, 365);
            showPage("mainPage");
            getUser();
            logoutButton.innerHTML = "Logout";
        }
    });
}

function getUser() {
    // Fetch user data from API
    api("me").then((res) => {
        if (res.message == 'success') {
            console.log(res);
        }
    });
}

const logoutButton = document.getElementById("logout");

function setLogoutButton(){
    if (getCookie("token")) {
        logoutButton.innerHTML = "Logout";
        console.log("you are currently logged in");
    } else {
        logoutButton.innerHTML = "Login";
        console.log("you are currently logged out");
    }
}

function buttonlogout() {
    if (getCookie("token")) {
        logout();
        console.log("logged out");
    } else {
        showPage("loginPage");
        console.log("go to login page");
    }
}


function logout(){
    deleteCookie("token");
    logoutButton.innerHTML = "Login";
    console.log("logged out");
}


// Helper functions

function showPage(id){
    let pages = document.getElementsByClassName("page");
    for(let i = 0; i < pages.length; i++){
        pages[i].style.display = "none";
    }
    document.getElementById(id).style.display = "block";
}

function bindEvents() {
    connectButton("register", register);
    connectButton("login", login);
    
    enableSubmits();
}

function enableSubmits(){
    document.body.addEventListener("keydown", function (e) {
        if (e.key == "Enter") { // if enter is pressed
            console.log(e);
            let target = e.target;
            while (target.getElementsByTagName("button").length == 0) {
                //console.log(target);
                target = target.parentElement;
            }
            target.getElementsByTagName("button")[0].click();
        }
    });
}

function connectButton(id, event) {
    let element = document.getElementById(id);
    if (element) {
        element.addEventListener("click", event);
    }
}

function getValue(id) {
    let element = document.getElementById(id);
    if (element) {
        return element.value;
    }
    return "";
}

function api(endpoint, method = 'GET', data = {}) {
    const API = "http://localhost:5000/";
    return fetch(API + endpoint, {
        method: method,
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + getCookie("token"),
        },
        body: method == 'GET' ? null : JSON.stringify(data),
    }).then((res) => res.json());
}

// Cookie functions stolen from w3schools (https://www.w3schools.com/js/js_cookies.asp)
function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + exdays * 24 * 60 * 60 * 1000);
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(";");
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == " ") {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function deleteCookie(cname) {
    setCookie(cname, "", -1);
}

bindEvents();
setLogoutButton();
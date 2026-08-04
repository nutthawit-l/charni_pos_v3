/* Project specific Javascript goes here. */
function getCookie(name) {
    const m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return m ? decodeURIComponent(m[2]) : null;
}

document.body.addEventListener("htmx:configRequest", (e) => {
    const token = getCookie("csrftoken") || getCookie("__Secure-csrftoken");
    if (token) e.detail.headers["X-CSRFToken"] = token;
});

htmx.config.responseHandling = [
    { code: "422", swap: true },
]

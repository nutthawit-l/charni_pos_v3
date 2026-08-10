/* Project specific Javascript goes here. */
function getCookie(name) {
  const m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return m ? decodeURIComponent(m[2]) : null;
}

document.body.addEventListener("htmx:configRequest", (e) => {
  const token = document.querySelector('meta[name="csrf-token"]')?.content;
  if (token) e.detail.headers["X-CSRFToken"] = token;
});

htmx.config.responseHandling.unshift({
  code: "422",
  swap: true,
  error: false,
});

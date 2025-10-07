const time = document.getElementById("spinner-value");
const min_time = 500;
const down_btn = document.getElementById("decrementBtn");
let val = Number(time.textContent);

function decrement() {
  if (val > min_time) val = val - 100;
  if (val <= min_time) down_btn.disabled = true;
  time.textContent = val;
}

function increment() {
  if (val <= min_time) down_btn.disabled = false;
  val = val + 100;
  time.textContent = val;
}

document.getElementById("dirs-form").addEventListener("submit", () => {
  document.getElementById("hiddenInput").value = val;
});

document.getElementById("spinner").addEventListener("wheel", (event) => {
  if (event.deltaY > 0) decrement();
  else increment();
});

document.querySelectorAll('input[name="favourite"]').forEach((radio) => {
  radio.addEventListener("change", (event) => {
    document.getElementById("hiddenInput").value = val;
    const form = new FormData(document.getElementById("dirs-form"));

    fetch("/get-favourites", {
      method: "POST",
      body: form,
    }).then((response) => {
      if (response.redirected) window.location.href = response.url;
    });
  });
});

window.addEventListener("load", () => {
  if (val <= min_time) down_btn.disabled = true;

  if (window.matchMedia('(display-mode: standalone)').matched || window.navigator.standalone === true) {
    this.document.querySelectorAll(".app").forEach(i => i.classList.add("webapp"));
  }
});
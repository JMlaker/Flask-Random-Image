let retryCount = 0;
const MAX_RETRIES = 3;

function loadNewImage() {
  const timestamp = new Date().getTime();
  const imgElement = document.getElementById("random-image");
  const imgName = document.getElementById("random-image-name");

  fetch("/random-image-url")
    .then((response) => response.json())
    .then((data) => {
      const img = new Image();

      img.onload = () => {
        imgElement.src = data.url + "?t=" + timestamp;
        imgName.textContent = data.filename;
        retryCount = 0;
      };
      img.onerror = () => {
        console.warn("Image fetch failed; trying again");
        retryIMG();
      };
      img.src = data.url;
    })
    .catch((err) => console.error("Failed to load new image:", err));
}

function retryIMG() {
  retryCount++;
  if (retryCount < MAX_RETRIES) {
    setTimeout(loadNewImage(), 5 * retryCount);
  } else {
    retryCount = 0;
  }
}

function trash() {
  const image = document.getElementById("random-image").src;

  fetch("/trash-image", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ img: image }),
  });

  loadNewImage();
}

let imgLoopId = null;

document.getElementById("autoimg").addEventListener("change", function () {
  if (this.checked) {
    imgLoopId = window.setInterval(loadNewImage, timer);
  } else {
    window.clearInterval(imgLoopId);
  }
});

document.getElementById("random-image").addEventListener("load", () => {
  const image = document.getElementById("random-image").src;

  fetch("/is-liked-img", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ img: image }),
  })
    .then((response) => response.json())
    .then((response) => {
      document.getElementById("like").checked = response.liked;
    });
});

document.getElementById("like").addEventListener("change", (e) => {
  const image = document.getElementById("random-image").src;

  fetch("/like-img", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ img: image, liked: e.target.checked }),
  });
});

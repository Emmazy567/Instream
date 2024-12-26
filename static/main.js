function startDownload() {
  const url = document.getElementById("video-url").value;

  if (!url) {
    alert("Please enter a valid URL.");
    return;
  }

  // Send the URL to the backend
  fetch("/download", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data.message);
      document.getElementById("progress-container").style.display = "block";
      updateProgress();
    });
}

function updateProgress() {
  fetch("/progress")
    .then((response) => response.json())
    .then((data) => {
      const percent = Math.round(data.percent);
      document.getElementById("progress-bar").value = percent;
      document.getElementById("progress-percent").innerText = percent + "%";

      // If the download is complete, show the download button
      if (percent >= 100) {
        const downloadButton = document.createElement("button");
        downloadButton.innerText = "Download Video";
        downloadButton.onclick = () => {
          window.location.href = "/get-file";
        };
        document.getElementById("progress-container").appendChild(downloadButton);
      } else {
        // Continue checking progress
        setTimeout(updateProgress, 1000);
      }
    });
}


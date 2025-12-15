function askData() {
  const query = document.getElementById("nlQuery").value;
  const resultBox = document.getElementById("nlResult");

  if (!query) {
    resultBox.innerHTML = "❗ Please enter a question.";
    return;
  }

  // Convert /report/<filename> → /ask/<filename>
  const askUrl = window.location.pathname.replace("/report/", "/ask/");

  fetch(askUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "query=" + encodeURIComponent(query),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        resultBox.innerHTML = "⚠️ " + data.error;
        return;
      }

      resultBox.innerHTML = `
        <div class="card">
          <h4>📢 Answer</h4>
          <p>${data.answer}</p>
        </div>
      `;
    })
    .catch(() => {
      resultBox.innerHTML = "❌ Error processing query.";
    });
}

// app/views/static/js/hint.js
import * as dom from "./dom.js";

export function initHint() {
  dom.hintBtn.addEventListener("click", () => {
    fetch("/hint")
      .then(r => r.json())
      .then(data => {
        document.querySelectorAll(".cell").forEach(c => c.classList.add("hint-dim"));
        data.hints.forEach(h => {
          const cell = document.querySelector(`.cell[data-row='${h.row}'][data-col='${h.col}']`);
          if (cell) {
            cell.classList.remove("hint-dim");
            cell.classList.add("hint-highlight");
          }
        });
        setTimeout(() => {
          document.querySelectorAll(".cell.hint-dim, .cell.hint-highlight")
                  .forEach(c => c.classList.remove("hint-dim","hint-highlight"));
        }, 5000);
      });
  });
}

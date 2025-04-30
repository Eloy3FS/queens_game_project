// app/views/static/js/timer.js
import * as dom from "./dom.js";

function parseTimeToSeconds(str) {
  const [m, s] = str.split(":").map(Number);
  return m * 60 + s;
}

export function startTimer() {
  clearInterval(window._timerInterval);
  fetch("/get_time")
    .then(r => r.json())
    .then(data => {
      dom.timerEl.textContent = data.elapsed_time;
      const base = parseTimeToSeconds(data.elapsed_time), t0 = Date.now();
      window._timerInterval = setInterval(() => {
        const d   = Math.floor((Date.now() - t0) / 1000);
        const tot = base + d;
        const mm  = Math.floor(tot / 60), ss = tot % 60;
        dom.timerEl.textContent = `${String(mm).padStart(2,"0")}:${String(ss).padStart(2,"0")}`;
      }, 1000);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const boardElement = document.getElementById("board");
    const resetBtn = document.getElementById("reset-btn");
    const boardSizeInput = document.getElementById("board-size");
    const timerElement = document.getElementById("timer");
    const statusMessage = document.getElementById("status-message");

    let boardSize = parseInt(boardSizeInput.value);

    function renderBoard(state) {
        // Suponiendo que el estado incluye una matriz con información de cada celda
        boardElement.innerHTML = "";
        // Actualiza la grid en base al tamaño actual
        boardElement.style.gridTemplateColumns = `repeat(${boardSize}, 1fr)`;
        for (let r = 0; r < boardSize; r++) {
            for (let c = 0; c < boardSize; c++) {
                const cell = document.createElement("div");
                cell.classList.add("cell");
                cell.dataset.row = r;
                cell.dataset.col = c;
                // Añade un contenido (podría ser la imagen de queen, cross, error según el estado)
                const cellContent = document.createElement("div");
                cellContent.classList.add("cell-content");
                // Por ahora, asigna un color base, luego se actualizará con datos
                cellContent.style.backgroundColor = "#fff";
                cell.appendChild(cellContent);

                // Agregar un event listener para el click
                cell.addEventListener("click", function() {
                    const row = cell.dataset.row;
                    const col = cell.dataset.col;
                    makeMove(row, col);
                });
                boardElement.appendChild(cell);
            }
        }
    }

    function makeMove(row, col) {
        // Realiza una petición AJAX para registrar el movimiento
        fetch("/move", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ row: row, col: col, move_type: "queen" })
        })
        .then(response => response.json())
        .then(data => {
            // Actualiza el estado del juego en la interfaz:
            updateBoard(data.state);
            statusMessage.textContent = data.message;
        })
        .catch(err => console.error("Error:", err));
    }

    function updateBoard(state) {
        // Usa el estado devuelto por el backend para actualizar cada celda,
        // el cronómetro, y otros elementos (este es un ejemplo básico)
        timerElement.textContent = state.elapsed_time;
        // Asumir que state.user_board es una matriz con el contenido (ej. "Q" o "X")
        const cells = document.querySelectorAll(".cell");
        cells.forEach(cell => {
            const row = cell.dataset.row;
            const col = cell.dataset.col;
            let cellContent = cell.firstChild;
            // Aquí podrás actualizar el background según el estado y asignar la imagen (usando cellContent.style.backgroundImage)
            if (state.user_board[row][col] === "Q") {
                cellContent.style.backgroundImage = "url(" + "/static/assets/queen.png" + ")";
            } else {
                cellContent.style.backgroundImage = "url(" + "/static/assets/cross.png" + ")";
            }
        });
    }

    // Función para reiniciar el juego
    resetBtn.addEventListener("click", function() {
        boardSize = parseInt(boardSizeInput.value);
        fetch("/reset", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ board_size: boardSize })
        })
        .then(response => response.json())
        .then(data => {
            updateBoard(data.state);
            renderBoard(data.state);
        })
        .catch(err => console.error("Error:", err));
    });

    // Inicializa el tablero (se puede hacer una petición para obtener el estado inicial)
    // Por ahora, se renderiza sin estado avanzado
    renderBoard({});
});

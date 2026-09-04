const API_BASE_URL = "http://127.0.0.1:8000";

const form = document.querySelector("#calculator-form");
const operationSelect = document.querySelector("#operation");
const powerFields = document.querySelector("#power-fields");
const numberFields = document.querySelector("#number-fields");
const numberLabel = document.querySelector("#number-label");
const numberInput = document.querySelector("#number-input");
const resultCard = document.querySelector("#result-card");
const resultValue = document.querySelector("#result-value");
const resultMeta = document.querySelector("#result-meta");
const message = document.querySelector("#message");
const historyEmpty = document.querySelector("#history-empty");
const historyTable = document.querySelector("#history-table");
const historyBody = document.querySelector("#history-body");
const refreshHistoryButton = document.querySelector("#refresh-history");

function setMessage(text = "") {
    message.textContent = text;
    message.classList.toggle("hidden", !text);
}

function updateFields() {
    const operation = operationSelect.value;
    const isPower = operation === "power";

    powerFields.classList.toggle("hidden", !isPower);
    numberFields.classList.toggle("hidden", isPower);

    if (operation === "fibonacci") {
        numberLabel.textContent = "Index n";
        numberInput.placeholder = "10";
    } else if (operation === "factorial") {
        numberLabel.textContent = "Număr n";
        numberInput.placeholder = "5";
    }
}

function getRequestData() {
    const operation = operationSelect.value;

    if (operation === "power") {
        const base = document.querySelector("#base").value;
        const exponent = document.querySelector("#exponent").value;

        if (base === "" || exponent === "") {
            throw new Error("Completează baza și exponentul.");
        }

        return {
            operation,
            payload: {
                base: Number(base),
                exponent: Number(exponent),
            },
        };
    }

    if (numberInput.value === "") {
        throw new Error("Completează valoarea lui n.");
    }

    return {
        operation,
        payload: { n: Number(numberInput.value) },
    };
}

function endpointFor(operation) {
    return `${API_BASE_URL}/${operation}`;
}

function showResult(data) {
    resultValue.textContent = data.result;
    resultMeta.textContent = `Operație: ${data.operation} · ID: ${data.id}`;
    resultCard.classList.remove("hidden");
}

function formatInput(input) {
    return JSON.stringify(input);
}

function renderHistory(history) {
    historyBody.innerHTML = "";
    historyEmpty.classList.toggle("hidden", history.length > 0);
    historyTable.classList.toggle("hidden", history.length === 0);

    history.forEach((request) => {
        const row = document.createElement("tr");
        const date = new Date(request.created_at).toLocaleString("ro-RO");

        row.innerHTML = `
            <td><span class="operation-pill">${request.operation}</span></td>
            <td><code>${formatInput(request.input)}</code></td>
            <td><strong>${request.result}</strong></td>
            <td class="date-cell">${date}</td>
        `;

        historyBody.appendChild(row);
    });
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/requests`);

        if (!response.ok) {
            throw new Error(`Istoricul nu a putut fi încărcat (${response.status}).`);
        }

        renderHistory(await response.json());
    } catch (error) {
        setMessage(`${error.message} Verifică dacă serverul FastAPI rulează.`);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage();
    resultCard.classList.add("hidden");

    try {
        const { operation, payload } = getRequestData();
        const response = await fetch(endpointFor(operation), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
            const detail = Array.isArray(data.detail)
                ? data.detail.map((item) => item.msg).join("; ")
                : data.detail || "Request invalid.";
            throw new Error(detail);
        }

        showResult(data);
        await loadHistory();
    } catch (error) {
        setMessage(error.message || "A apărut o eroare neașteptată.");
    }
});

operationSelect.addEventListener("change", updateFields);
refreshHistoryButton.addEventListener("click", loadHistory);

updateFields();
loadHistory();

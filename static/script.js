function showModal() {
    const modal = document.getElementById("modal");
    const overlay = document.getElementById("modal-overlay");

    if (modal && overlay) {
        modal.classList.remove("hidden");
        overlay.classList.remove("hidden");
    } else {
        console.error("No se encontró el modal o overlay.");
    }
}

function hideModal() {
    const modal = document.getElementById("modal");
    const overlay = document.getElementById("modal-overlay");

    if (modal && overlay) {
        modal.classList.add("hidden");
        overlay.classList.add("hidden");
    }
}

function exportToPDF() {
    const resultsDiv = document.getElementById("results");
    if (!resultsDiv || !resultsDiv.innerHTML.trim()) {
        alert("No hay resultados para exportar.");
        return;
    }

    fetch("/results", { method: "GET" })
        .then(response => {
            if (!response.ok) throw new Error("Error al obtener los datos del escaneo.");
            return response.json();
        })
        .then(data => {
            return fetch("/export/pdf", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            }).then(res => {
                if (!res.ok) throw new Error("Fallo al generar el PDF desde Flask.");
                return res.json();
            });
        })
        .then(file => {
            const downloadLink = document.getElementById("downloadLink");
            if (downloadLink) {
                downloadLink.href = "/download_pdf/" + file.file;
            } else {
                console.error("No se encontró el elemento 'downloadLink'");
            }
            showModal();
        })
        .catch(err => {
            console.error("Error al generar PDF:", err);
            alert("No se pudo generar el PDF. Inténtalo nuevamente.");
        });
}

function showHistory() {
    const historyDiv = document.getElementById("history");
    const tbody = document.getElementById("history-body");

    if (!historyDiv || !tbody) {
        console.error("No se encontró el historial o tabla de contenido.");
        return;
    }

    historyDiv.classList.toggle("hidden");

    if (!historyDiv.classList.contains("hidden")) {
        fetch("/historial")
            .then(res => {
                if (!res.ok) throw new Error("Fallo al cargar el historial.");
                return res.json();
            })
            .then(rows => {
                tbody.innerHTML = "";
                rows.forEach(row => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>${row[0]}</td>
                        <td>${row[1]}</td>
                        <td>${row[2]}</td>
                        <td>${row[3]}</td>
                        <td>${row[5]}</td>
                        <td>${row[6]}</td>
                        <td><button onclick="deleteScan(${row[0]})"><i class="fas fa-trash"></i></button></td>`;
                    tbody.appendChild(tr);
                });
            })
            .catch(err => {
                console.error("Error al cargar historial:", err);
                tbody.innerHTML = "<tr><td colspan='7'>Error al cargar historial.</td></tr>";
            });
    }
}

function deleteScan(scanId) {
    if (confirm("¿Estás seguro de eliminar este registro?")) {
        fetch(`/delete/${scanId}`, {
            method: "POST"
        }).then(() => showHistory());
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const scanForm = document.getElementById("scanForm");
    const loader = document.getElementById("loader");
    const results = document.getElementById("results");

    if (!scanForm || !loader || !results) {
        console.warn("Algunos elementos no se cargaron correctamente.");
        return;
    }

    scanForm.addEventListener("submit", function(e) {
        e.preventDefault();

        loader.classList.remove("hidden");
        results.innerHTML = "";

        const formData = {
            ip: document.getElementById("ip").value,
            start_port: parseInt(document.getElementById("start_port").value),
            end_port: parseInt(document.getElementById("end_port").value)
        };

        fetch("/scan", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) throw new Error("Error en la solicitud de escaneo.");
            return response.json();
        })
        .then(data => {
            let html = `<h2><i class="fas fa-server"></i> Resultados del escaneo en ${data.ip}</h2>`;
            html += `<p>Puertos abiertos: ${data.total_open} | Duración: ${data.duration}</p>`;
            html += `<ul>`;
            data.open_ports.forEach(port => {
                const banner = data.banners[port] || "Desconocido";
                const description = data.port_descriptions[port] || "Desconocido";
                const vulnerabilities = data.vulnerabilities[port]?.join(", ") || "Ninguna";
                html += `
                    <li title="${description} | Vuln.: ${vulnerabilities}">
                        <i class="fas fa-plug"></i> Puerto <strong>${port}</strong> ➜ ABIERTO | Banner: "${banner}" | Vuln.: ${vulnerabilities}
                    </li>`;
            });
            html += `</ul>`;
            results.innerHTML = html;
        })
        .catch(error => {
            console.error("Error:", error);
            results.innerHTML = `<p>Error al realizar el escaneo: ${error.message}</p>`;
        })
        .finally(() => {
            loader.classList.add("hidden"); // Ocultar loader
        });
});

// Cerrar modal al hacer clic fuera de él
const modalOverlay = document.getElementById("modal-overlay");
if (modalOverlay) {
    modalOverlay.addEventListener("click", function(event) {
        if (event.target === this) {
            hideModal();
        }
    });
}})
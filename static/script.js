document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectBtn = document.getElementById('select-btn');
    const statusSection = document.getElementById('status-section');
    const previewSection = document.getElementById('preview-section');
    const feedbackSection = document.getElementById('feedback-section');
    const resultsLayout = document.getElementById('results-layout');
    const uploadSection = document.querySelector('.upload-section');
    const feedbackContent = document.getElementById('feedback-content');
    const resetBtn = document.getElementById('reset-btn');

    // Trigger file selection
    selectBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleUpload(e.target.files[0]);
        }
    });

    // Drag and Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#d4af37';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length > 0) {
            handleUpload(e.dataTransfer.files[0]);
        }
    });

    async function handleUpload(file) {
        // Show layout, hide upload
        uploadSection.classList.add('hidden');
        resultsLayout.classList.remove('hidden');
        statusSection.classList.remove('hidden');
        feedbackSection.classList.add('hidden');

        // Show video preview
        const videoElement = document.getElementById('player-video');
        videoElement.src = URL.createObjectURL(file);
        videoElement.load();

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Analysis failed');
            }

            const data = await response.json();
            displayFeedback(data.feedback);
        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
            resetUI();
        }
    }

    function displayFeedback(text) {
        statusSection.classList.add('hidden');
        feedbackSection.classList.remove('hidden');

        // Convert Markdown table to HTML table
        let html = text;

        if (text.includes('|')) {
            const lines = text.trim().split('\n');
            let tableHtml = '<table><thead><tr>';

            // Header
            const headers = lines[0].split('|').filter(cell => cell.trim() !== '');
            headers.forEach(h => tableHtml += `<th>${h.trim()}</th>`);
            tableHtml += '</tr></thead><tbody>';

            // Rows (skip index 1 as it's the separator |---|)
            for (let i = 2; i < lines.length; i++) {
                if (!lines[i].includes('|')) continue;
                tableHtml += '<tr>';
                const cells = lines[i].split('|').filter(cell => cell.trim() !== '');
                cells.forEach(c => tableHtml += `<td>${c.trim()}</td>`);
                tableHtml += '</tr>';
            }
            tableHtml += '</tbody></table>';
            html = tableHtml;
        } else {
            // Fallback for non-table output
            html = text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');
        }

        feedbackContent.innerHTML = html;
    }

    resetBtn.addEventListener('click', resetUI);

    function resetUI() {
        resultsLayout.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        fileInput.value = '';
    }
});

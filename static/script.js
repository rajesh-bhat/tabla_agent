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

        console.log('Received text:', text);
        console.log('Text type:', typeof text);

        try {
            // Try to parse as JSON
            const analysis = JSON.parse(text);
            console.log('Parsed JSON successfully:', analysis);

            // Create HTML table from JSON
            const html = `
                <table class="analysis-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Agent's Assessment</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Taal Identification</strong></td>
                            <td>${analysis.taal_identification}</td>
                        </tr>
                        <tr>
                            <td><strong>Sam Analysis</strong></td>
                            <td>${analysis.sam_analysis}</td>
                        </tr>
                        <tr>
                            <td><strong>Tempo (BPM)</strong></td>
                            <td>${analysis.tempo_bpm}</td>
                        </tr>
                    </tbody>
                </table>
            `;

            console.log('Generated HTML table');
            feedbackContent.innerHTML = html;
        } catch (e) {
            // Fallback: display as plain text if JSON parsing fails
            console.error('JSON parse error:', e);
            console.error('Failed text:', text);
            feedbackContent.innerHTML = `<pre>${text}</pre>`;
        }
    }

    resetBtn.addEventListener('click', resetUI);

    function resetUI() {
        resultsLayout.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        fileInput.value = '';
    }
});

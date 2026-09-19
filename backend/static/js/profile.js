function setupUploader(kind){
    const overlay  = document.getElementById(`upload-overlay-${kind}`);
    const dropzone = document.getElementById(`dropzone-${kind}`);
    const input    = document.getElementById(`file-${kind}`);
    const crop = AdderCrop.attach(overlay, kind === 'avatar' ? { aspect: 1, maxSize: 600 } : { aspect: 3, maxSize: 1800 });
    let hasFile = false;

    document.querySelector(`[data-target="${kind}"]`).addEventListener('click', () => overlay.hidden = false);
    overlay.querySelector('[data-close]').addEventListener('click', () => overlay.hidden = true);

    dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', e => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        handleFile(e.dataTransfer.files[0]);
    });
    input.addEventListener('change', e => handleFile(e.target.files[0]));

    function handleFile(file){
        if(!file) return;
        hasFile = true;
        crop.load(file);
    }

    overlay.querySelector('[data-save]').addEventListener('click', async () => {
        if(!hasFile) return;
        const blob = await crop.blob();
        if(!blob) return;
        const formData = new FormData();
        formData.append(kind === 'avatar' ? 'profile_img' : 'background_img', blob, crop.filename());

        const res = await fetch(overlay.dataset.uploadUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
            body: formData,
        });
        if(res.ok) location.reload();
    });
}

setupUploader('avatar');
setupUploader('background');

function setupUploader(kind){
    const overlay  = document.getElementById(`upload-overlay-${kind}`);
    const dropzone = document.getElementById(`dropzone-${kind}`);
    const input    = document.getElementById(`file-${kind}`);
    const crop = AdderCrop.attach(overlay, kind === 'avatar' ? { aspect: 1, maxSize: 600 } : { aspect: 3, maxSize: 1800 });
    let hasFile = false;

    // Cancel, backdrop click and Esc all discard the pick so the next open starts empty
    function close(){
        overlay.hidden = true;
        hasFile = false;
        input.value = '';
        crop.reset();
    }

    document.querySelector(`[data-target="${kind}"]`).addEventListener('click', () => overlay.hidden = false);
    overlay.querySelector('[data-close]').addEventListener('click', close);
    overlay.addEventListener('click', e => { if(e.target === overlay) close(); });
    document.addEventListener('keydown', e => { if(e.key === 'Escape' && !overlay.hidden) close(); });

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

    // Remove: back to the default picture/banner
    overlay.querySelector('[data-remove]').addEventListener('click', async () => {
        if(!confirm('Remove this image and use the default?')) return;
        const formData = new FormData();
        formData.append('remove', kind === 'avatar' ? 'profile_img' : 'background_img');
        const res = await fetch(overlay.dataset.uploadUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
            body: formData,
        });
        if(res.ok) location.reload();
    });

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

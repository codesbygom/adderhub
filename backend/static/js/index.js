//sidebar
const menuItems=document.querySelectorAll('.menu-item');

const changeActiveItem=() =>{
    menuItems.forEach(item => {
        item.classList.remove('active');
    })
}


menuItems.forEach(item =>{
    item.addEventListener('click', () => {
        changeActiveItem();
        item.classList.add('active');
    })
})

//post upload overlay (sidebar "Upload Post" button)
function setupPostUploader(){
    const openBtn = document.getElementById('open-post-upload');
    if(!openBtn) return;

    const overlay  = document.getElementById('upload-overlay-post');
    const dropzone = document.getElementById('dropzone-post');
    const input    = document.getElementById('file-post');
    const caption  = document.getElementById('caption-post');
    const preview  = overlay.querySelector('.preview');
    let selectedFile = null;

    openBtn.addEventListener('click', () => overlay.hidden = false);
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
        selectedFile = file;
        preview.src = URL.createObjectURL(file);
        preview.hidden = false;
    }

    overlay.querySelector('[data-save]').addEventListener('click', async () => {
        if(!selectedFile) return;
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('caption', caption.value);

        const res = await fetch(overlay.dataset.uploadUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
            body: formData,
        });
        if(res.ok) location.reload();
    });
}

setupPostUploader();


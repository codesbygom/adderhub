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
    const crop     = AdderCrop.attach(overlay, { aspect: 1, maxSize: 1600 });
    let hasFile = false;

    overlay.querySelectorAll('[data-aspect]').forEach(btn => btn.addEventListener('click', () => {
        overlay.querySelectorAll('[data-aspect]').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        crop.setAspect(parseFloat(btn.dataset.aspect));
    }));

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
        hasFile = true;
        crop.load(file);
    }

    overlay.querySelector('[data-save]').addEventListener('click', async () => {
        if(!hasFile) return;
        const blob = await crop.blob();
        if(!blob) return;
        const formData = new FormData();
        formData.append('image', blob, crop.filename());
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


function setupPostMenus() {
    const closeAll = (except) => {
        document.querySelectorAll('.post-menu-dropdown').forEach((dd) => {
            if (dd === except) return;
            dd.hidden = true;
            dd.previousElementSibling.setAttribute('aria-expanded', 'false');
        });
    };

    document.addEventListener('click', (e) => {
        const toggle = e.target.closest('.post-menu-toggle');
        if (!toggle) {
            closeAll();
            return;
        }
        const dd = toggle.nextElementSibling;
        closeAll(dd);
        dd.hidden = !dd.hidden;
        toggle.setAttribute('aria-expanded', String(!dd.hidden));
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeAll();
    });
}

setupPostMenus();

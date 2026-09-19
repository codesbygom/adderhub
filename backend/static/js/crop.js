// Shared crop/zoom helper for the avatar, banner and post uploaders.
// Wraps Cropper.js (loaded from the CDN in base.html).
//   const crop = AdderCrop.attach(overlay, { aspect: 1, maxSize: 512 });
//   crop.load(file)          -> shows the crop area for that file
//   crop.setAspect(4 / 5)    -> change the crop ratio (post uploader)
//   await crop.blob()        -> cropped Blob (or null) for uploading
window.AdderCrop = {
    attach(overlay, { aspect, maxSize }) {
        const img   = overlay.querySelector('.preview');
        const tools = overlay.querySelector('.crop-tools');
        let cropper = null;
        let mime = 'image/jpeg';

        tools?.querySelectorAll('[data-zoom]').forEach((btn) => {
            btn.addEventListener('click', () => cropper?.zoom(parseFloat(btn.dataset.zoom)));
        });
        tools?.querySelector('[data-reset]')?.addEventListener('click', () => cropper?.reset());

        return {
            load(file) {
                cropper?.destroy();
                mime = file.type === 'image/png' ? 'image/png' : 'image/jpeg';
                img.hidden = false;
                img.src = URL.createObjectURL(file);
                cropper = new Cropper(img, {
                    aspectRatio: aspect,
                    viewMode: 1,          // crop box stays inside the image
                    dragMode: 'move',     // drag = pan the image; wheel/pinch = zoom
                    autoCropArea: 1,
                    background: false,
                    responsive: true,
                });
                if (tools) tools.hidden = false;
            },
            setAspect(ratio) {
                cropper?.setAspectRatio(ratio);
            },
            blob() {
                if (!cropper) return Promise.resolve(null);
                const canvas = cropper.getCroppedCanvas({
                    maxWidth: maxSize,
                    maxHeight: maxSize,
                    imageSmoothingQuality: 'high',
                });
                return new Promise((resolve) => canvas.toBlob(resolve, mime, 0.92));
            },
            filename() {
                return mime === 'image/png' ? 'cropped.png' : 'cropped.jpg';
            },
        };
    },
};

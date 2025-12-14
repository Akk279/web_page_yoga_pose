// Simple shared camera controller used by Session and Lessons pages
// Exposes a global CameraModule.createController(options)
(function(){
  function createController(options){
    const video = options.video;
    const canvas = options.canvas; // 224x224 upload buffer (can be hidden)
    const apiBaseInput = options.apiBaseInput;
    const onPrediction = options.onPrediction || function(){};
    const onStatus = options.onStatus || function(){}; // {camera:'On'|'Off'|'Error', analyzing:boolean}
    const intervalMs = options.intervalMs || 1000;

    const ctx = canvas.getContext('2d');
    let stream = null;
    let timer = null;

    async function start(){
      try{
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        video.srcObject = stream;
        if (video.play) video.play();
        onStatus({ camera: 'On', analyzing: false });
        if (options.autoPredict !== false) startAutoPredict();
      }catch(e){
        onStatus({ camera: 'Error', analyzing: false, error: e });
        throw e;
      }
    }

    function stop(){
      stopAutoPredict();
      if (stream){
        for (const t of stream.getTracks()) t.stop();
        stream = null;
      }
      video.srcObject = null;
      onStatus({ camera: 'Off', analyzing: false });
    }

    async function predict(){
      if (!video.srcObject) return null;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.9));
      const fd = new FormData();
      fd.append('file', blob, 'frame.jpg');
      const base = (apiBaseInput && apiBaseInput.value ? apiBaseInput.value : '').replace(/\/$/, '');
      const url = (base || '') + '/predict';
      const resp = await fetch(url, { method: 'POST', body: fd });
      const data = await resp.json();
      onPrediction(data, resp.ok);
      return { data, ok: resp.ok };
    }

    function startAutoPredict(){
      stopAutoPredict();
      onStatus({ camera: 'On', analyzing: true });
      timer = setInterval(() => { predict().catch(()=>{}); }, intervalMs);
    }

    function stopAutoPredict(){
      if (timer){
        clearInterval(timer); timer = null;
      }
      onStatus({ camera: stream ? 'On' : 'Off', analyzing: false });
    }

    // Expand/collapse support (fullscreen and in-place)
    let previousInline = { width: '', height: '', objectFit: '' };
    let inPlaceExpanded = false;
    function applyFullscreenSizing(inFullscreen){
      if (inFullscreen){
        // Store previous inline styles to restore later
        previousInline.width = video.style.width;
        previousInline.height = video.style.height;
        previousInline.objectFit = video.style.objectFit;
        // Fill viewport while preserving aspect ratio
        video.style.width = '100vw';
        video.style.height = '100vh';
        video.style.objectFit = 'contain';
        video.style.backgroundColor = '#000';
      } else {
        video.style.width = previousInline.width || '';
        video.style.height = previousInline.height || '';
        video.style.objectFit = previousInline.objectFit || '';
      }
    }

    function isFs(){
      return !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
    }

    function reqFs(el){
      (el.requestFullscreen || el.webkitRequestFullscreen || el.msRequestFullscreen || function(){})();
    }

    function exitFs(){
      (document.exitFullscreen || document.webkitExitFullscreen || document.msExitFullscreen || function(){})();
    }

    function toggleFullscreen(){
      const el = video; // use the video element for consistent sizing
      if (!isFs()){
        reqFs(el);
        setTimeout(() => applyFullscreenSizing(true), 50);
      } else {
        exitFs();
        setTimeout(() => applyFullscreenSizing(false), 50);
      }
    }

    // In-place expansion (not fullscreen): enlarge video then restore
    function expandInPlace(size = { width: 720, height: 540 }){
      if (inPlaceExpanded) return true;
        previousInline.width = video.style.width;
        previousInline.height = video.style.height;
        previousInline.objectFit = video.style.objectFit;
        video.style.width = `${size.width}px`;
        video.style.height = `${size.height}px`;
        video.style.objectFit = 'cover';
        inPlaceExpanded = true;
      try { options.onFullscreenChange && options.onFullscreenChange(true); } catch(_) {}
      return true;
    }

    function collapseInPlace(){
      if (!inPlaceExpanded) return false;
      video.style.width = previousInline.width || '';
      video.style.height = previousInline.height || '';
      video.style.objectFit = previousInline.objectFit || '';
      inPlaceExpanded = false;
      try { options.onFullscreenChange && options.onFullscreenChange(false); } catch(_) {}
      return false;
    }

    function toggleExpand(size = { width: 720, height: 540 }){
      return inPlaceExpanded ? collapseInPlace() : expandInPlace(size);
    }

    // Listen for fullscreen changes to adjust sizing
    ['fullscreenchange','webkitfullscreenchange','MSFullscreenChange'].forEach(evt => {
      document.addEventListener(evt, () => {
        const inFs = isFs();
        applyFullscreenSizing(inFs);
        try { options.onFullscreenChange && options.onFullscreenChange(inFs); } catch(_) {}
      });
    });

    return { start, stop, predict, startAutoPredict, stopAutoPredict, toggleFullscreen, toggleExpand, expandInPlace, collapseInPlace };
  }

  window.CameraModule = { createController };
})();



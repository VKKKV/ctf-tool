setTimeout(() => {
    console.log("Auto Wheel Down");
    window.archGreybeardLoop = setInterval(() => {
        let fakeEvent = new MouseEvent('mousemove', {
            view: window,
            bubbles: true,
            cancelable: true,
            // 用微小的随机数代替死板的 0 和 -1，防止某些愚蠢的 JS 脚本检测固定规律
            clientX: Math.floor(Math.random() * 10),
            clientY: Math.floor(Math.random() * 10)
        });
        document.dispatchEvent(fakeEvent);
    }, 1000);
}, 5000);
// clearInterval(window.archGreybeardLoop);

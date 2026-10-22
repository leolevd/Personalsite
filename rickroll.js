function rickroll() {
    document.body.innerHTML = ""
    let video = document.createElement("video")
    video.src = "vid.mp4"
    video.autoplay = true
    video.muted = false
    video.playsInline = true
    video.controls = false
    document.body.appendChild(video)

    video.play().catch(() => {
        video.controls = true
    })
}
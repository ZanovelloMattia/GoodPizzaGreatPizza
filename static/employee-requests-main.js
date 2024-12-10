const requests = document.querySelectorAll(".request");

requests.forEach(request => {
    try {
    const acceptBtn = request.querySelector('.accept-btn');
    acceptBtn.addEventListener('click', accept);
    } catch  {
    }

    const declineBtn = request.querySelector('.decline-btn');
    declineBtn.addEventListener('click', decline);
})

async function accept() {
    const request = this.closest(".request");
    const requestId = request.querySelector(".id").textContent;

    try {
        const response = await fetch('/accept-request', {
            method: 'post',
            body: requestId
        })
        window.location.href = '/requests'
    } catch (err) {
        console.error('error: ', err)
    }
}

async function decline() {
    const request = this.closest(".request");
    const requestId = request.querySelector(".id").textContent;

    try {
        const response = await fetch('/decline-request', {
            method: 'post',
            body: requestId
        })
        window.location.href = '/requests'
    } catch (err) {
        console.error('error: ', err)
    }
}

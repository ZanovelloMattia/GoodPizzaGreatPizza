let employees = document.querySelectorAll(".employee");
let days = document.querySelectorAll(".day");
let dragItem = null;
let dropped = false;
let draggedFrom = null;

const loadBtn = document.getElementById("upload-shifts");
const pdfBtn = document.getElementById("download-pdf");
const imgBtn = document.getElementById("download-img");

const selectTimestamp = document.getElementById("select-timestamp");
const error = document.getElementById('shifts-error');

employees.forEach(employee => {
    employee.addEventListener("dragstart", dragStart);
    employee.addEventListener("dragend", dragEnd);
})

days.forEach(day => {
    day.addEventListener("dragover", dragOver)
    day.addEventListener("dragenter", dragEnter)
    day.addEventListener("dragleave", dragLeave)
    day.addEventListener("drop", drop)
})

function dragStart() {
    //console.log("drag start")
    dragItem = this;
    draggedFrom = this.parentNode;
}

function dragEnd() {
    //console.log("drag end")
    if (!dropped) {
        if (!draggedFrom.classList.contains('employees')) {
            dragItem.remove()
        }
    }
    dropped = false
}

function dragOver(e) {
    e.preventDefault();
    const scrollMargin = 100;
    const speed = 10;

    if (window.innerHeight - e.clientY < scrollMargin) {
        window.scrollBy(0, speed);
    }

    if (e.clientY < scrollMargin) {
        window.scrollBy(0, -speed);
    }
}

function dragEnter() {
    //console.log("drag enter")
}

function dragLeave() {
    //console.log("drag leave")
}

function drop() {
    //console.log("drop")
    if (draggedFrom.classList.contains('employees')) {
        clonedNode = dragItem.cloneNode(true)
        clonedNode.addEventListener("dragstart", dragStart);
        clonedNode.addEventListener("dragend", dragEnd);
        this.append(clonedNode)
    } else {
        this.append(dragItem)
    }
    dropped = true
}

loadBtn.addEventListener('click', async () => {
    canLoad = true;
    days.forEach(day => {
        if (day.childElementCount != 4) {
            canLoad = false;
        }
    })
    if (!canLoad) {
        error.style.display = 'block';
        error.querySelector('p').textContent = "Per ogni giorno ci devono essere esattamente 3 turni"
        return;
    }

    shifts = {}
    for (let i = 0; i < days.length; i++) {
        let day = days[i];
        let dayShifts = {};
        for (let j = 1; j < day.childElementCount; j++) {
            employee = day.children[j]
            employeeID = employee.querySelector(".id").textContent.split('#')[0]
            
            dayShifts[(j - 1).toString()] = employeeID;
        }
        shifts["day" + (i + 1)] = dayShifts;
    }

    try {
        console.log(shifts)
        const response = await fetch('/shifts', {
            method: 'post',
            body: JSON.stringify(shifts)
        })
        console.log("completed", response);
        window.location.href = '/shifts'
    } catch (err) {
        console.error("error: ", err);
    }
})

selectTimestamp.addEventListener('change', () => {
    url = "/shifts?timestamp=" + selectTimestamp.value;
    window.location.href = encodeURI(url);
})

pdfBtn.addEventListener('click', () => {
    url = "/download/pdf?timestamp=" + selectTimestamp.value;
    window.location.href = encodeURI(url);
})

imgBtn.addEventListener('click', () => {
    url = "/download/img?timestamp=" + selectTimestamp.value;
    window.location.href = encodeURI(url);
})
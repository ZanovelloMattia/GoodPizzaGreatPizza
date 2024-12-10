let employees = document.querySelectorAll('.employee');
let days = document.querySelectorAll('.day');

const dropArea1 = document.getElementById('drop-area-1');
const dropArea2 = document.getElementById('drop-area-2');
const askButton = document.getElementById('ask-button');

const timestamp = document.getElementById('timestamp').textContent;

const pdfBtn = document.getElementById("download-pdf");
const imgBtn = document.getElementById("download-img");

const employeeId = document.getElementById('employee-id').textContent;

const swapEerror = document.getElementById('swap-error');

let dropIndex1 = -1;
let employee1 = -1;
let dropIndex2 = -1;
let employee2 = -1;

let fromDay1 = null;
let fromDay2 = null;

let dragItem = null;
let canDrop = true;
let same = false;
let draggedFrom = null;

employees.forEach(employee => {
    employee.addEventListener('dragstart', dragStart);
    employee.addEventListener('dragend', dragEnd);
})

dropArea1.addEventListener('drop', dropInDropArea);
dropArea1.addEventListener('dragover', dragOver);

dropArea2.addEventListener('drop', dropInDropArea);
dropArea2.addEventListener('dragover', dragOver);

askButton.addEventListener('click', askChange);

function dragStart() {
    dragItem = this;
    draggedFrom = this.parentNode;
}

function dragEnd() {
    if (draggedFrom.classList.contains('drop-area') && !same) {
        dragItem.remove();
        draggedFrom.classList.remove('drop-area-full');
        paragraph = document.createElement('p');
        paragraph.textContent = 'Trascina qui un dipendente';
        draggedFrom.append(paragraph);
    }
    same = false
    updateAskButton();
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

    if (draggedFrom.getAttribute('id') === this.getAttribute('id')) {
        console.log("niger")
        canDrop = false
    } else {
        console.log("white")
        canDrop = true
    }
}

function dropInDropArea() {
    if (this.id === 'drop-area-1' && dragItem.querySelector('.id').textContent !== employeeId) {
        swapEerror.style.display = 'block';
        swapEerror.querySelector('p').textContent = "Nella prima casella puoi mettere solo tuoi turni"
        return;
    } else if (this.id === 'drop-area-2' && dragItem.querySelector('.id').textContent === employeeId) {
        swapEerror.style.display = 'block';
        swapEerror.querySelector('p').textContent = "Nella seconda casella puoi mettere solo turni altrui"
        return;
    }

    clonedNode = dragItem.cloneNode(true)
    clonedNode.addEventListener('dragstart', dragStart);
    clonedNode.addEventListener('dragend', dragEnd);
    clonedNode.classList.add('swap-employee');

    if (this.id === 'drop-area-1' && draggedFrom.id === 'drop-area-1' || this.id === 'drop-area-2' && draggedFrom.id === 'drop-area-2') {
        same = true
    }

    this.textContent = '';
    this.classList.add('drop-area-full')
    this.append(clonedNode);
    if (!(draggedFrom.id === 'drop-area-1' || draggedFrom.id === 'drop-area-2')) {
        index = Array.from(dragItem.parentNode.children).indexOf(dragItem) - 1
        if (this.id === 'drop-area-1') {
            employee1 = dragItem.querySelector('.id').textContent;

            dropIndex1 = index;
            fromDay1 = draggedFrom;
        } else {
            employee2 = dragItem.querySelector('.id').textContent;
            dropIndex2 = index;
            fromDay2 = draggedFrom;
        }
    }
}

function updateAskButton() {
    askButton.disabled = !(dropArea1.children[0].tagName === "DIV" && dropArea2.children[0].tagName === "DIV");
}

async function askChange() {
    const idQuestionerDay = fromDay1.querySelector(".id").textContent;
    const idQuestionedDay = fromDay2.querySelector(".id").textContent;

    try {
        const response = await fetch('/make-request', {
            method: 'post',
            body: JSON.stringify({
                'questioner_id': employee1,
                'questioner_day_id': idQuestionerDay,
                'questioner_index': dropIndex1,
                'questioned_id': employee2,
                'questioned_day_id': idQuestionedDay,
                'questioned_index': dropIndex2
            })
        })
        console.log('completed', response)
        window.location.href = '/shifts'
    } catch (err) {
        console.error('error: ', err)
    }
}

pdfBtn.addEventListener('click', () => {
    url = "/download/pdf?timestamp=" + timestamp;
    window.location.href = encodeURI(url);
})

imgBtn.addEventListener('click', () => {
    url = "/download/img?timestamp=" + timestamp;
    window.location.href = encodeURI(url);
})
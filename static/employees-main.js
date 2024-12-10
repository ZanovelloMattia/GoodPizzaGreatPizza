const newError = document.getElementById('new-emplyee-error')
const modifyEerror = document.getElementById('modify-emplyee-error')

document.getElementById("add-employee").addEventListener("click", function() {
    const newSection = document.getElementById("new-employee");
    newSection.style.display = "flex"
})

// TODO: add reload with out redirect

document.getElementById("load-employee").addEventListener("click", async function(e) {
    const newEmployee = this.closest(".new-form");
    const nameInput = newEmployee.querySelector('#name-input').value;
    const surnameInput = newEmployee.querySelector('#surname-input').value;
    const birthdateInput = newEmployee.querySelector('#birthdate-input').value;

    if (nameInput === '' || surnameInput === '' || birthdateInput === '' || birthdateInput.length !== 10) {
        newError.style.display = 'block';
        newError.querySelector('p').textContent = "Inserisci solo valori validi"
        return;
    }

    try {
        const response = await fetch('/add-employee', {
            method: 'post',
            body: JSON.stringify({'name': nameInput, 'surname': surnameInput, 'birthdate': birthdateInput})
        })
        console.log("completed", response);
        window.location.href = "/employees";
    } catch (err) {
        console.error("error: ", err)
    }

})

document.querySelectorAll('.edit-btn').forEach(button => {
    button.addEventListener('click', function () {
        const employee = this.closest('.employee');
        const editSection = employee.querySelector('.edit-section');
        const profileInfo = employee.querySelector('.profile-info');
        const actions = employee.querySelector('.actions');

        editSection.style.display = 'block';
        profileInfo.style.display = 'none';
        actions.style.display = 'none';
    });
});

document.querySelectorAll('.cancel-modification-btn').forEach(button => {
    button.addEventListener('click', function () {
        const employee = this.closest('.employee');
        const editSection = employee.querySelector('.edit-section');
        const profileInfo = employee.querySelector('.profile-info');
        const actions = employee.querySelector('.actions');

        editSection.style.display = 'none';
        profileInfo.style.display = 'block';
        actions.style.display = 'block';
    });
});

document.querySelectorAll('.save-btn').forEach(button => {
    button.addEventListener('click', async function () {
        const employee = this.closest('.employee');
        const nameInput = employee.querySelector('#name-input').value;
        const surnameInput = employee.querySelector('#surname-input').value;
        const birthdateInput = employee.querySelector('#birthdate-input').value;
        const employeeID = employee.querySelector('.id').textContent;

        if (nameInput === '' || surnameInput === '' || birthdateInput === '' || birthdateInput.length !== 10) {
            modifyEerror.style.display = 'block';
            modifyEerror.querySelector('p').textContent = "Inserisci solo valori validi"
            return;
        }

        try {
            const response = await fetch('/modify-employee', {
                method: 'post',
                body: JSON.stringify({'name': nameInput, 'surname': surnameInput, 'birthdate': birthdateInput, 'id': employeeID})
            })
            console.log("completed", response)
            window.location.href = "/employees"
        } catch (err) {
            console.error("error: ", err)
        }

    });
});

document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', async function () {
        const employee = this.closest('.employee');
        const employeeID = employee.querySelector('.id').textContent;
        
        try {
            const response = await fetch('/delete-employee', {
                method: 'post',
                body: employeeID
            })
            console.log("completed", response)
            window.location.href = "/employees"
        } catch (err) {
            console.error("error: ", err)
        }
    });
});
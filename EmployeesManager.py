import DatabaseManager as DB
import datetime

home_html_template = ""
employees_page_html_template = ""
employee_html_template = ""

def generate_html_employees(id):
    # Funzione per generare l'HTML della pagina degli impiegati
    global home_html_template, employees_page_html_template, employee_html_template
    
    # Ottiene tutti gli impiegati della pizzeria dal database
    employees = DB.get_all_pizzeria_employees(id)

    employees_html = ""

    # Genera il codice HTML per ogni impiegato
    for employee_id, employee in employees.items():
        # Formatta la data di nascita
        birthdate = datetime.datetime.strftime(employee["birthdate"], "%d/%m/%Y")
        not_formatted_birthdate = datetime.datetime.strftime(employee['birthdate'], "%Y-%m-%d")
        # Sostituisce i placeholder nel template con i dati dell'impiegato
        employees_html += (employee_html_template.replace("%name%", employee["name"])
                           .replace("%surname%", employee["surname"])
                           .replace("%birthdate%", birthdate)
                           .replace('%not-formatted-birthdate%', not_formatted_birthdate)
                           .replace("%id%", str(employee_id))
                           .replace('%hours%', str(calculate_employee_hours(id, employee_id))))

    # Inserisce gli impiegati generati nel contenuto della pagina
    content = employees_page_html_template.replace("%employees%", employees_html)
    # Genera la pagina finale sostituendo i placeholder principali
    final_html = (home_html_template.replace("%content%", content)
                  .replace("%title%", "Employees")
                  .replace("%style-path%", "employees-style.css")
                  .replace("%pizzeria-name%", DB.get_pizzeria(id)["name"])
                  .replace("%home-active%", "")
                  .replace("%shifts-active%", "")
                  .replace("%employees-active%", "active"))
    return final_html

def calculate_employee_hours(id_pizzeria, id_employee):
    timestamps = DB.get_all_pizzeria_timestamps(id_pizzeria)
    
    if len(timestamps) == 0:
        return 0
    
    last_timestamp = timestamps[0]
    
    shifts = DB.get_shift_from_timestamp(id_pizzeria, last_timestamp)
    
    hours = 0
    
    for day in shifts.values():
        for employee in day.values():
            if id_employee == employee['id']:
                hours += 1
            
    return hours


def init():
    # Inizializza i template caricandoli dai file corrispondenti
    global home_html_template, employees_page_html_template, employee_html_template
    with open("template/main-page.html") as f:
        home_html_template = f.read()
    with open("template/employees/employees-page.html") as f:
        employees_page_html_template = f.read()
    with open("template/employees/employee.html") as f:
        employee_html_template = f.read()
    

if __name__ == "__main__":
    # Punto di ingresso del programma, inizializza i template
    init()

import DatabaseManager as DB
import datetime

main_html_employee_template = ''
page_html_template = ''
request_html_template = ''
pending_request_template = ''

num_to_day = {
    0: 'Lunedì',
    1: 'Martedì',
    2: 'Mercoledì',
    3: 'Giovedì',
    4: 'Venerdì',
}

def get_html_requests(employee_id) -> str:
    # Funzione per generare l'HTML delle richieste di un dipendente
    global main_html_employee_template, page_html_template, request_html_template, pending_request_template

    employee = DB.get_employee(employee_id)  # Recupera i dati del dipendente
    pizzeria = DB.get_pizzeria(employee['id_pizzeria'])  # Recupera i dati della pizzeria associata

    # Ottiene le richieste ricevute dal dipendente
    requests = DB.get_questioned_requests(employee_id)
    # Ottiene le richieste pendenti fatte dal dipendente
    pending_requests = DB.get_questioner_requests(employee_id)
    
    request_html = ''
    
    print("bobmbo clasrt")
    
    # Cicla sulle richieste ricevute e genera l'HTML per ognuna
    for request_id, request in requests.items():  # TODO: calcolare il giorno specifico
        timestamp = request['timestamp']
        shifts = DB.get_shift_from_timestamp(employee['id_pizzeria'], timestamp)
        
        request_from = DB.get_employee(request['ID_questioner'])  # Ottiene il dipendente che ha fatto la richiesta
        questioned_day = DB.get_day(request['ID_questioned_day'])  # Ottiene il giorno corrente del dipendente ricevente
        questioned_index = request['questioned_index']  # Ottiene il turno corrente
        questioner_day = DB.get_day(request['ID_questioner_day'])  # Ottiene il giorno desiderato dal richiedente
        questioner_index = request['questioner_index']  # Ottiene il turno desiderato
        
        questioned_day_index = 0
        questioner_day_index = 0
        counter = 0
            
        for day_id in shifts.keys():
            print(day_id)
            if day_id == request['ID_questioned_day']:
                questioned_day_index = counter
            if day_id == request['ID_questioner_day']:
                questioner_day_index = counter
            counter += 1
        
        # Sostituisce i placeholder nel template con i dati reali
        request_html += (request_html_template.replace('%name%', request_from['name'])
                         .replace('%surname%', request_from['surname'])
                         .replace('%current-day%', num_to_day[questioned_day_index])
                         .replace('%current-shift%', f"{str(questioned_index)}°")
                         .replace('%desired-day%', num_to_day[questioner_day_index])
                         .replace('%desired-shift%', f"{str(questioner_index)}°")
                         .replace('%id%', str(request_id)))
    
    # Cicla sulle richieste pendenti e genera l'HTML per ognuna
    for pending_request_id, pending_request in pending_requests.items():
        shifts = DB.get_shift_from_timestamp(employee['id_pizzeria'], pending_request['timestamp'])

        
        request_to = DB.get_employee(pending_request['ID_questioned'])  # Ottiene il dipendente destinatario
        questioner_index = pending_request['questioner_index']  # Ottiene il turno corrente
        questioned_index = pending_request['questioned_index']  # Ottiene il turno desiderato
        
        questioner_day_index = 0
        questioned_day_index = 0
        counter = 0
        
        for day_id in shifts.keys():
            print(day_id)
            if day_id == pending_request['ID_questioned_day']:
                questioned_day_index = counter
            if day_id == pending_request['ID_questioner_day']:
                questioner_day_index = counter
            counter += 1
        
        # Sostituisce i placeholder nel template con i dati reali
        request_html += (pending_request_template.replace('%name%', request_to['name'])
                         .replace('%surname%', request_to['surname'])
                         .replace('%current-day%', num_to_day[questioner_day_index])
                         .replace('%current-shift%', f"{str(questioner_index)}°")
                         .replace('%desired-day%', num_to_day[questioned_day_index])
                         .replace('%desired-shift%', f"{str(questioned_index)}°")
                         .replace('%id%', str(pending_request_id)))
    
    # Inserisce tutte le richieste nel contenuto della pagina
    content = page_html_template.replace('%requests%', request_html)
    
    # Sostituisce i placeholder principali per la pagina dell'impiegato
    final_html = (main_html_employee_template.replace('%title%', 'Richieste')
                  .replace('%employee-id%', str(employee_id))
                  .replace('%shifts-active%', '')
                  .replace('%request-active%', 'active')
                  .replace('%content%', content)
                  .replace('%style-path%', 'employee-requests-style.css')
                  .replace("%pizzeria-name%", pizzeria["name"]))
    
    return final_html


def accept_request(request_id: int) -> str:
    # Funzione per accettare una richiesta e aggiornare i dati nel database
    request = DB.get_request(request_id)
    
    # Estrae le informazioni dalla richiesta
    id_questioner_day = request['ID_questioner_day']
    questioner_index = request['questioner_index']
    id_questioned_day = request['ID_questioned_day']
    questioned_index = request['questioned_index']
    
    # Ottiene i giorni coinvolti nello scambio
    questioner_day = DB.get_day(id_questioner_day)
    questioned_day = DB.get_day(id_questioned_day)
    
    # Costruisce le chiavi per accedere ai turni dei dipendenti
    key1 = 'ID_employee' + str(questioner_index)
    key2 = 'ID_employee' + str(questioned_index)
        
    # Scambia i turni tra i due dipendenti
    questioner_day[key1], questioned_day[key2] = questioned_day[key2], questioner_day[key1]
    
    # Aggiorna i dati dei giorni nel database
    DB.update_day(id_questioner_day, questioner_day['ID_employee1'], questioner_day['ID_employee2'], questioner_day['ID_employee3'])
    DB.update_day(id_questioned_day, questioned_day['ID_employee1'], questioned_day['ID_employee2'], questioned_day['ID_employee3'])
    
    # Elimina la richiesta una volta accettata
    DB.delete_request(request_id)


def init():
    # Inizializza i template caricandoli dai file corrispondenti
    global main_html_employee_template, page_html_template, request_html_template, pending_request_template
    with open('template/employee-main-page.html') as f:
        main_html_employee_template = f.read()
    with open('template/employee-requests/request.html') as f:
        request_html_template = f.read()
    with open('template/employee-requests/pending-request.html') as f:
        pending_request_template = f.read()
    with open("template/employee-requests/requests-page.html") as f:
        page_html_template = f.read()

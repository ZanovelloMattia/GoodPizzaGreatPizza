import DatabaseManager as DB
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from DatabaseManager import get_pizzeria_name
from PIL import Image, ImageDraw, ImageFont
import io
import json

week_shifts = {}  # Dizionario globale per memorizzare i turni settimanali

# Template HTML globali utilizzati per generare le pagine HTML
home_html_template = ""
shifts_page_html_template = ""
day_html_template = ""
day_comp_html_template = ""
no_employees_html_template = ""
employee_main_html_template = ""
employee_shifts_page = ""
employee_day_html_template = ""
employee_day_comp_html_template = ""
no_shifts_html_template = ""

num_to_day = {
    0: 'Lunedì',
    1: 'Martedì',
    2: 'Mercoledì',
    3: 'Giovedì',
    4: 'Venerdì',
}

def load_shifts(id: int, timestamp: datetime) -> bool:
    global week_shifts
    week_shifts = {}  # Reset dei turni settimanali

    shifts = DB.get_shift_from_timestamp(id, timestamp)  # Ottiene i turni dal database usando un timestamp
    print("shiftsssss", shifts)
    
    if shifts is None:  # Controlla se i turni esistono
        return False
    
    employees_dict = {}  # TODO: Aggiungere supporto per ridurre le query al database
    counter = 0
    for day_key, shifts in shifts.items():  # Itera sui turni per ogni giorno
        day = {}
        for shift, employee in shifts.items():  # Itera sui turni e recupera i dettagli degli impiegati
            print(employee)
            day[str(employee['id']) +  "#" + str(counter)] = DB.get_employee(employee['id'])
            counter += 1
        week_shifts[day_key] = day  # Memorizza i turni della giornata nel dizionario globale
    print(week_shifts)
    return True

def generate_shifts(id: int) -> bool:  # TODO: Aggiungere casualità nella generazione dei turni
    global week_shifts

    week_shifts = {}  # Reset dei turni settimanali

    employees_dict = DB.get_all_pizzeria_employees(id)  # Recupera tutti gli impiegati della pizzeria
    employees_keys = list(employees_dict.keys())  # Ottiene le chiavi (ID impiegati)

    if len(employees_keys) == 0:  # Se non ci sono impiegati, restituisce False
        return False

    counter = 0

    for i in range(1, 6):  # Genera turni per 5 giorni
        day_shifts = {}
        for j in range(3):  # Genera 3 turni per giorno
            index = counter % len(employees_keys)
            day_shifts[str(employees_keys[index]) +  "#" + str(counter)] = employees_dict[employees_keys[index]]
            counter += 1
        week_shifts["day" + str(i)] = day_shifts  # Memorizza i turni generati
    print(week_shifts)
    return True

def generate_html_employees(id: int) -> str:
    global day_comp_html_template

    employees_dict = DB.get_all_pizzeria_employees(id)  # Recupera tutti gli impiegati della pizzeria
    employees_html = ""

    for key, employee in employees_dict.items():  # Genera HTML per ogni impiegato
        employees_html += (day_comp_html_template.replace("%name%", employee["name"])
                           .replace("%surname%", employee["surname"])
                           .replace("%id%", str(key))
                           .replace("%only-id%", str(key)))
        
    return employees_html

def generate_html_shifts(id: int, timestamp: datetime = None) -> str:
    global week_shifts, home_html_template, shifts_page_html_template, day_html_template, day_comp_html_template, no_employees_html_template
    
    if timestamp is None:
        succeded = generate_shifts(id)  # Genera turni se il timestamp non è fornito
    else:
        succeded = load_shifts(id, timestamp)  # Carica turni esistenti
    
    if not succeded:  # Se non ci sono turni o dipendenti
        final_html = (home_html_template.replace("%style-path%", "shifts-style.css")
                      .replace("%title%", "Turni")
                      .replace("%content%", no_employees_html_template)
                      .replace("%pizzeria-name%", DB.get_pizzeria(id)["name"])
                      .replace("%home-active%", "")
                      .replace("%shifts-active%", "active")
                      .replace("%employees-active%", ""))
        return final_html

    day_html = ""

    counter = 0

    for day_key, day in week_shifts.items():  # Genera HTML per ogni giorno della settimana
        day_html += day_html_template.replace("%day-title%", num_to_day[counter])
        day_comps = ""
        for key, employee in day.items():  # Genera HTML per i turni di ogni giorno
            day_comps += (day_comp_html_template.replace("%name%", employee["name"])
                          .replace("%surname%", employee["surname"])
                          .replace("%id%", str(key))
                          .replace("%only-id%", str(key).split('#')[0]))

        day_html = day_html.replace("%day-comps%", day_comps)
        counter += 1

    timestamps = DB.get_all_pizzeria_timestamps(id)  # Recupera i timestamp dei turni dal database

    if len(timestamps) == 0:  # Se non ci sono timestamp, calcola l'inizio e la fine della settimana corrente
        timestamps_html = ""
        now = datetime.datetime.now()

        start_of_week = now - datetime.timedelta(days=now.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        start_of_week = datetime.datetime.strftime(start_of_week, "%d/%m/%Y")
        end_of_week = datetime.datetime.strftime(end_of_week, "%d/%m/%Y")
    else:  # Genera HTML per i timestamp disponibili
        timestamps_html_template = "<option value=\"%timestamp-datetime%\" id=\"%id_shift%\" %selected%>%timestamp%</option>"
        timestamps_html = ""

        for list_timestamp in timestamps:
            formatted_timestamp = datetime.datetime.strftime(list_timestamp, "%d/%m/%Y %H:%M:%S")
            str_timestamp = datetime.datetime.strftime(list_timestamp, "%Y-%m-%d %H:%M:%S.%f")
            if timestamp is not None:
                if list_timestamp == timestamp:
                    timestamps_html += (timestamps_html_template.replace("%timestamp%", formatted_timestamp)
                                        .replace("%timestamp-datetime%", str_timestamp)
                                        .replace("%selected%", "selected"))
                else:
                    timestamps_html += (timestamps_html_template.replace("%timestamp%", formatted_timestamp)
                                        .replace("%timestamp-datetime%", str_timestamp)
                                        .replace("%selected%", ""))
            else:
                timestamps_html += (timestamps_html_template.replace("%timestamp%", formatted_timestamp)
                                    .replace("%timestamp-datetime%", str_timestamp)
                                    .replace("%selected%", ""))
                
        start_of_week = timestamps[0] - datetime.timedelta(days=timestamps[0].weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        start_of_week = datetime.datetime.strftime(start_of_week, "%d/%m/%Y")
        end_of_week = datetime.datetime.strftime(end_of_week, "%d/%m/%Y")

    content = (shifts_page_html_template.replace("%days%", day_html)
               .replace("%employees%", generate_html_employees(id))
               .replace("%start-week%", start_of_week)
               .replace("%end-week%", end_of_week)
               .replace("%options%", timestamps_html))

    final_html = (home_html_template.replace("%style-path%", "shifts-style.css")
                  .replace("%title%", "Turni").replace("%content%", content)
                  .replace("%pizzeria-name%", DB.get_pizzeria(id)["name"])
                  .replace("%home-active%", "").replace("%shifts-active%", "active")
                  .replace("%employees-active%", ""))
    return final_html

def generate_html_employee_shifts(id: int) -> str:
    global employee_main_html_template, employee_shifts_page, employee_day_html_template, employee_day_comp_html_template, no_shifts_html_template
    
    employee = DB.get_employee(id)  # Recupera i dati del dipendente
    pizzeria = DB.get_pizzeria(employee['id_pizzeria'])  # Recupera i dati della pizzeria associata
    
    timestamps = DB.get_all_pizzeria_timestamps(employee['id_pizzeria'])  # Recupera i timestamp dei turni
    
    if len(timestamps) == 0:  # Se non ci sono turni disponibili
        final_html = (employee_main_html_template.replace("%style-path%", "shifts-style.css")
                      .replace("%title%", "Turni")
                      .replace("%content%", no_shifts_html_template)
                      .replace("%pizzeria-name%", pizzeria["name"])
                      .replace("%home-active%", "")
                      .replace("%shifts-active%", "active"))
        return final_html
        
    last_timestamp = timestamps[0]  # Prende l'ultimo timestamp disponibile
    
    db_employee = DB.get_employee(id)  # Verifica se il dipendente esiste nel database

    if db_employee is None:  # Se il dipendente non esiste
        final_html = (employee_main_html_template.replace("%style-path%", "shifts-style.css")
                      .replace("%title%", "Turni")
                      .replace("%content%", no_shifts_html_template)
                      .replace("%pizzeria-name%", pizzeria["name"])
                      .replace("%home-active%", "")
                      .replace("%shifts-active%", "active"))
        return final_html
    
    id_pizzeria = db_employee['id_pizzeria']
    print(last_timestamp)
    shifts = DB.get_shift_from_timestamp(id_pizzeria, last_timestamp)  # Recupera i turni associati al timestamp
    print(shifts)
    day_html = ""

    counter = 0

    for day_id, day in shifts.items():  # Genera HTML per ogni giorno
        day_html += employee_day_html_template.replace("%day-title%", num_to_day[counter])
        day_comps = ""
        for key, employee in day.items():  # Genera HTML per i turni giornalieri
            day_comps += (employee_day_comp_html_template.replace("%name%", employee["name"])
                          .replace("%surname%", employee["surname"])
                          .replace("%id%", str(employee["id"])))

        day_html = day_html.replace("%day-comps%", day_comps).replace("%id%", str(day_id))
        counter += 1
        
    start_of_week = last_timestamp - datetime.timedelta(days=last_timestamp.weekday())  # Calcola inizio settimana
    end_of_week = start_of_week + datetime.timedelta(days=6)  # Calcola fine settimana

    start_of_week = datetime.datetime.strftime(start_of_week, "%d/%m/%Y")
    end_of_week = datetime.datetime.strftime(end_of_week, "%d/%m/%Y")

    str_timestamp = datetime.datetime.strftime(last_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    content = (employee_shifts_page.replace("%days%", day_html)
               .replace("%employees%", generate_html_employees(id))
               .replace("%start-week%", start_of_week)
               .replace("%end-week%", end_of_week)
               .replace('%timestamp%', str_timestamp))

    final_html = (employee_main_html_template.replace("%style-path%", "shifts-style.css")
                  .replace("%title%", "Turni").replace("%content%", content)
                  .replace("%pizzeria-name%", pizzeria["name"])
                  .replace("%home-active%", "").replace("%shifts-active%", "active")
                  .replace("%employees-active%", "")
                  .replace("%employee-id%", str(id)))
    return final_html

    
def create_shift_pdf(ID_pizzeria, timestamp):

    shift_dict = DB.get_shift_from_timestamp(ID_pizzeria, timestamp)
    
    print(shift_dict)
    
    print("shiftsDict", shift_dict)

    pizzeria_name = get_pizzeria_name(ID_pizzeria)
    
    # Calcolo data di inizio validità (giorno e ora del timestamp)
    start_date = timestamp.strftime("%d/%m/%Y %H:%M:%S")
    
    # Calcolo data di fine validità (aggiungi 4 giorni)
    end_date_obj = timestamp + datetime.timedelta(days=5)
    end_date = end_date_obj.strftime("%d/%m/%Y %H:%M:%S")

    formatted_timestamp = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    # Crea il nome del file PDF
    safe_pizzeria_name = pizzeria_name.replace("/", "-")
    
    buffer = io.BytesIO()

    # Crea il PDF
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Titolo
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Report dei turni di {pizzeria_name}")
    
    # Aggiunta delle date di validità
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"   Data inizio validità: {start_date}")
    c.drawString(100, 710, f"   Data fine validità: {end_date}")

    #Giorni e dipendenti
    y_position = 680  
    counter = 0
    for day_key, day_info in shift_dict.items():
        if y_position < 50:  # Controlla se serve una nuova pagina
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 750
        
        # Titolo del giorno
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_position, f"{num_to_day[counter]}:")
        y_position -= 20
        
        # Dati dei dipendenti
        c.setFont("Helvetica", 11)
        for i in range(3):
            emp = day_info[str(i)]
            c.drawString(120, y_position, f"Dipendente {i + 1}° turno: {emp['name']} {emp['surname']} (ID: {emp['id']})")
            y_position -= 20
        
        # Disegna una linea divisoria
        c.line(80, y_position + 10, 500, y_position + 10)
        y_position -= 10
        counter += 1

    # Salva il PDF
    c.save()
    buffer.seek(0)
    return buffer


def create_shift_image(ID_pizzeria, timestamp):
    """
    Genera un'immagine PNG con i dati dei turni.
    """
    # Recupera il nome della pizzeria
    pizzeria_name = get_pizzeria_name(ID_pizzeria)

    shift_dict = DB.get_shift_from_timestamp(ID_pizzeria, timestamp)

    print(shift_dict)
    # Preparazione delle date
    
    start_date = timestamp.strftime("%d/%m/%Y %H:%M:%S")
    end_date_obj = timestamp + datetime.timedelta(days=5)
    end_date = end_date_obj.strftime("%d/%m/%Y %H:%M:%S")

    # Creazione dell'immagine
    img_width, img_height = 800, 800  # Dimensioni immagine
    background_color = "white"
    text_color = "black"

    # Font di default (cambia il percorso per un font personalizzato)
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_subtitle = ImageFont.truetype("arial.ttf", 18)
        font_text = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        # Usa il font di default se Arial non è disponibile
        font_title = font_subtitle = font_text = ImageFont.load_default()

    # Creazione immagine vuota
    img = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(img)

    # Titolo
    y_position = 20
    draw.text((20, y_position), f"Report dei turni di {pizzeria_name}", fill=text_color, font=font_title)
    y_position += 40

    # Date
    draw.text((20, y_position), f"  Data inizio validità: {start_date}", fill=text_color, font=font_subtitle)
    y_position += 30
    draw.text((20, y_position), f"  Data fine validità: {end_date}", fill=text_color, font=font_subtitle)
    y_position += 40

    # Turni
    counter = 0
    for day_key, day_info in shift_dict.items():
        if y_position > img_height - 50:  # Se finisce lo spazio, crea una nuova immagine
            img.save(f"{pizzeria_name}_shifts_part.png")
            img = Image.new("RGB", (img_width, img_height), background_color)
            draw = ImageDraw.Draw(img)
            y_position = 20

        # Giorno
        draw.text((20, y_position), f"{num_to_day[counter]}:", fill=text_color, font=font_subtitle)
        y_position += 30

        # Dettagli turni
        for i in range(3):
            emp = day_info[str(i)]
            draw.text((40, y_position),
                      f"Dipendete {i + 1}° turno: {emp['name']} {emp['surname']} (ID: {emp['id']})",
                      fill=text_color, font=font_text)
            y_position += 20

        # Divider
        y_position += 10
        draw.line((20, y_position, img_width - 20, y_position), fill="gray", width=1)
        y_position += 10
        counter += 1

    # Salva l'immagine
    formatted_timestamp = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    safe_pizzeria_name = pizzeria_name.replace("/", "-")
    
    img_buffer = io.BytesIO()
    
    img.save(img_buffer, format='PNG')

    img_buffer.seek(0)

    return img_buffer

def init():
    # Definizione delle variabili globali per i template HTML
    global home_html_template, shifts_page_html_template, day_html_template, day_comp_html_template, no_employees_html_template
    global employee_main_html_template, employee_shifts_page, employee_day_html_template, employee_day_comp_html_template, no_shifts_html_template

    # Carica il template della pagina principale dalla directory dei template
    with open("template/main-page.html") as f:
        home_html_template = f.read()

    # Carica il template della pagina dei turni
    with open("template/shifts/shifts-page.html") as f:
        shifts_page_html_template = f.read()

    # Carica il template per i turni di un singolo giorno
    with open("template/shifts/day.html") as f:
        day_html_template = f.read()

    # Carica il template per la componente di un turno (ad esempio, un turno singolo di un impiegato)
    with open("template/shifts/day-comp.html") as f:
        day_comp_html_template = f.read()

    # Carica il template che indica l'assenza di dipendenti
    with open("template/shifts/no-employees.html") as f:
        no_employees_html_template = f.read()

    # Carica il template della pagina principale dell'impiegato
    with open("template/employee-main-page.html") as f:
        employee_main_html_template = f.read()

    # Carica il template della pagina dei turni specifici per un impiegato
    with open("template/employee-shifts/shifts-page.html") as f:
        employee_shifts_page = f.read()

    # Carica il template per i turni giornalieri di un singolo impiegato
    with open("template/employee-shifts/day.html") as f:
        employee_day_html_template = f.read()

    # Carica il template per la componente di un turno giornaliero specifico per un impiegato
    with open("template/employee-shifts/day-comp.html") as f:
        employee_day_comp_html_template = f.read()

    # Carica il template che indica l'assenza di turni per un impiegato
    with open("template/employee-shifts/no-shifts.html") as f:
        no_shifts_html_template = f.read()


def main():
    DB.open()
    DB.init()
    shift_example = {
    "day1": {
        "0": {"id": 1, "name": "Alice", "surname": "Smith"},
        "1": {"id": 2, "name": "Bob", "surname": "Johnson"},
        "2": {"id": 3, "name": "Charlie", "surname": "Brown"}
    },
    "day2": {
        "0": {"id": 4, "name": "Dana", "surname": "Lee"},
        "1": {"id": 5, "name": "Evan", "surname": "Kim"},
        "2": {"id": 6, "name": "Fay", "surname": "Wu"}
    }
}

    create_shift_image("1","22/04/2022 00:00:00", shift_example)
    DB.close()

if __name__ == "__main__":
    main()
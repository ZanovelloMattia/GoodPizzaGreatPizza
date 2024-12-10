from http.server import BaseHTTPRequestHandler, HTTPServer
import DatabaseManager as DB
import ShiftsManager as SM
import EmployeesManager as EM
import RequestsManager as RM
import urllib.parse as urlParser
import os
import json
import uuid
import datetime
import traceback
import time
import Logger

web_server: HTTPServer

# Configurazioni per la durata della sessione
expiring_year_add = 0
expiring_month_add = 0
expiring_day_add = 0
expiring_hour_add = 2
expiring_minute_add = 0

html_pages = {}
css_files = {}
js_files = {}
immages = {}
sessions = {}

class Server_handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parsing della richiesta GET per ottenere il percorso e i parametri
        url = urlParser.urlparse(self.path)
        path = url.path
        self.get = self.parse_entry_list(url.query, "&", "=")  # Decodifica i parametri GET

        Logger.log("GET PATH" + path)

        # Gestione delle risorse statiche CSS
        if "static" + path in css_files:
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            # Invia il contenuto del file CSS richiesto
            self.wfile.write(bytes(css_files["static" + path], 'utf-8'))
            Logger.log("STATIC RESPONSE")
            return

        # Gestione delle risorse statiche JS
        if "static" + path in js_files:
            self.send_response(200)
            self.send_header('Content-type', 'text/javascript')
            self.end_headers()
            # Invia il contenuto del file JavaScript richiesto
            self.wfile.write(bytes(js_files["static" + path], 'utf-8'))
            Logger.log("STATIC RESPONSE")
            return

        # Gestione delle immagini statiche
        if "static" + path in immages:
            self.send_response(200)
            self.send_header('Content-type', 'immagine/png')
            self.end_headers()
            # Invia l'immagine richiesta
            self.wfile.write(immages["static" + path])
            Logger.log("STATIC RESPONSE")
            return

        # Definizione delle rotte disponibili per GET
        routes = {
            "/logout": self.logout,
            "/shifts": self.shifts,
            "/employees": self.employees,
            "/requests": self.requests,
            "/": self.home
        }

        # Rotte accessibili senza autenticazione
        not_logget_routes = {
            "/login": self.login,
            "/register": self.register,
            "/employee-login": self.employee_login
        }
        
        download_routes = {
            '/download/pdf': self.download_pdf,
            '/download/img': self.download_img,
        }

        self.cookie = None
        self.auth = None
        self.redirect = None

        try:
            # Parsing dei cookie per gestire la sessione
            cookies = self.parse_entry_list(self.headers["Cookie"], ";", "=")
            sessio_id, session = self.get_session(cookies)

            if session:  # Se la sessione esiste
                self.auth = cookies['uuid']
                self.permission = int(session['permission'])
                self.id = int(session['ID'])

                if path in download_routes:
                    buffer, type, f_name = download_routes[path]()
                    self.send_response(200)
                    self.send_header('Content-Type', type)
                    self.send_header('Content-Disposition', f"attachment; filename={f_name}")
                    self.end_headers()

                    # Invia il PDF direttamente al browser
                    self.wfile.write(buffer.read())
                    return
                if path in not_logget_routes:  # Evita accesso a pagine per utenti non loggati
                    self.redirect = '/'
                    response, content = self.home()
                    response = 302  # Redirect
                else:
                    response, content = routes[path]()  # Gestisce la richiesta sulla rotta specificata
            else:  # Nessuna sessione attiva
                if path in not_logget_routes:  # Consentito solo per rotte non loggate
                    response, content = not_logget_routes[path]()
                else:
                    self.redirect = '/login'  # Reindirizza al login
                    response, content = self.login()
                    response = 302
        except Exception as error:  # Gestione degli errori
            print("GET error", error)
            traceback.print_exc()
            response = 404  # Risorsa non trovata
            content = "Not Found"

        # Costruisce e invia la risposta HTTP
        self.send_response(response)
        self.send_header('Content-type', 'text/html')

        if self.redirect is not None:  # Aggiunge un header per il redirect se necessario
            self.send_header('Location', self.redirect)

        if self.cookie:  # Aggiunge un cookie di sessione se presente
            self.send_header('Set-Cookie', self.cookie)

        self.end_headers()
        self.wfile.write(bytes(content, 'utf-8'))  # Invia il contenuto della risposta
        
        Logger.log("GET RESPONDED")

    def do_POST(self):
        # Parsing del percorso richiesto tramite POST
        path = urlParser.urlparse(self.path).path
        Logger.log("POST PATH" + path)

        # Definizione delle rotte disponibili per POST
        routes = {
            "/logout": self.logout_post,
            "/shifts": self.shifts_post,
            "/add-employee": self.add_employee,
            "/modify-employee": self.modify_employee,
            "/delete-employee": self.delete_employee,
            "/make-request": self.make_request,
            "/accept-request": self.accept_request,
            "/decline-request": self.decline_request,
            "/": self.home
        }

        # Rotte accessibili senza autenticazione
        not_logget_routes = {
            "/login": self.login_post,
            "/register": self.register_post,
            "/employee-login": self.employee_login_post
        }

        self.cookie = None
        self.auth = None
        self.redirect = None

        try:
            # Parsing dei cookie per controllare la sessione
            cookies = self.parse_entry_list(self.headers["Cookie"], ";", "=")
            sessio_id, session = self.get_session(cookies)

            if session:  # Se la sessione è valida
                self.auth = cookies['uuid']
                self.permission = int(session['permission'])
                self.id = int(session['ID'])
                
                if path in not_logget_routes:  # Gestisce le rotte pubbliche
                    self.redirect = '/'
                    response, content = self.home()
                    response = 302
                else:
                    Logger.log("STO PER CHIAMARE LA FUNZIONE")
                    response, content = routes[path]()  # Esegue la funzione associata alla rotta
            else:  # Nessuna sessione valida
                if path in not_logget_routes:
                    response, content = not_logget_routes[path]()  # Rotta pubblica
                else:
                    self.redirect = '/login'  # Reindirizza al login
                    response, content = self.login()
                    response = 302
        except Exception as error:  # Gestione errori
            print("POST error", error)
            traceback.print_exc()
            response = 404
            content = "Not Found"
        
        Logger.log("ARRIVATO PRIMA SEND RESPONSE")
        
        # Invio della risposta HTTP
        self.send_response(response)
        self.send_header('Content-type', 'text/html')

        if self.redirect is not None:  # Gestisce il redirect
            self.send_header('Location', self.redirect)

        if self.cookie:  # Gestisce il cookie
            self.send_header('Set-Cookie', self.cookie)

        self.end_headers()
        self.wfile.write(bytes(content, 'utf-8'))  # Invia il contenuto della risposta

        Logger.log("REDY FOR A NEW POST REQUEST")

    def login(self):
        # Restituisce la pagina HTML del login con eventuali messaggi di errore nascosti
        return 200, html_pages['static/login.html'].replace('%display-error%', 'none')
    
    def login_post(self):
        # Recupera la lunghezza dei dati POST inviati
        content_length = int(self.headers["Content-length"])
        # Decodifica i dati POST
        post_data = self.parse_entry_list(self.rfile.read(content_length).decode(), "&", "=")
        
        # Controlla che i campi necessari siano presenti
        if not "owner_name" in post_data or not "name" in post_data:
            return 200, html_pages['static/login.html'].replace('%display-error%', 'block').replace(
                '%error%', 'Inserisci sia il nome del gestore che quello della pizzeria!')

        # Decodifica i valori dei parametri
        owner_name = urlParser.unquote_plus(post_data['owner_name'])
        name = urlParser.unquote_plus(post_data['name'])

        # Verifica che il nome del proprietario della pizzeria esista nel database
        db_owner_name = DB.get_pizzeria_owner(name)
        if db_owner_name is None:
            # Restituisce un errore se il nome non corrisponde a nessuna pizzeria registrata
            return 200, html_pages['static/login.html'].replace('%display-error%', 'block').replace(
                '%error%', 'Nome del gestore o nome della pizzeria sbagliato!')

        # Confronta il nome del proprietario fornito con quello salvato nel database
        if owner_name == db_owner_name:
            # Genera una sessione valida
            generated_uuid, expiring_date = self.generate_session()
            self.cookie = f"uuid={generated_uuid}"

            # Recupera l'ID della pizzeria e salva la sessione nel database
            self.id = DB.get_pizzeria_from_name(name)["ID_pizzeria"]
            DB.insert_session(generated_uuid, self.id, 0, expiring_date)
            self.permission = 0  # Imposta i permessi del gestore (livello 0)

            # Reindirizza alla home con il login effettuato
            self.redirect = "/"
            response, content = self.home()
            return 302, content.replace('%display-error%', 'none')

        # Restituisce un errore in caso di mismatch nei dati forniti
        return 200, html_pages['static/login.html'].replace('%display-error%', 'block').replace(
            '%error%', 'Nome del gestore o nome della pizzeria sbagliato!')

    def logout(self):
        # Controlla che l'utente sia autenticato
        if not self.auth:
            self.redirect = "/"
            return 302, html_pages['static/login.html']
        
        # Cancella il cookie e rimuove la sessione dal database
        self.cookie = "uuid="
        DB.delete_session_from_uuid(self.auth)
        self.redirect = "/"
        return 302, html_pages['static/login.html'].replace('%display-error%', 'none')

    def logout_post(self):
        # Funzione analoga a `logout`, ma progettata per richieste POST
        if not self.auth:
            self.redirect = "/"
            return 302, html_pages['static/login.html']
        
        # Cancella il cookie e la sessione
        self.cookie = "uuid="
        DB.delete_session_from_uuid(self.auth)
        self.redirect = "/"
        return 302, html_pages['static/login.html'].replace('%display-error%', 'none')

    def register(self):
        # Restituisce la pagina HTML per la registrazione
        return 200, html_pages['static/register.html'].replace('%display-error%', 'none')

    def register_post(self):
        # Recupera la lunghezza dei dati POST e li decodifica
        content_length = int(self.headers["Content-length"])
        post_data = self.parse_entry_list(self.rfile.read(content_length).decode(), "&", "=")

        # Controlla che i campi obbligatori siano presenti
        if not "owner_name" in post_data or not "name" in post_data:
            return 200, html_pages['static/register.html'].replace('%display-error%', 'block').replace(
                '%error%', 'Inserisci sia il nome del gestore che quello della pizzeria!')

        # Decodifica i valori dei campi
        owner_name = urlParser.unquote_plus(post_data['owner_name'])
        name = urlParser.unquote_plus(post_data['name'])
        
        # Verifica che i campi non siano vuoti
        if name == '' or owner_name == '':
            return 200, html_pages['static/register.html'].replace('%display-error%', 'block').replace(
                '%error%', 'Inserisci sia il nome del gestore che quello della pizzeria!')
        
        # Controlla se una pizzeria con lo stesso nome è già registrata
        pizzeria_already_exist = DB.get_pizzeria_from_name(name)
        if pizzeria_already_exist is not None:
            return 200, html_pages['static/register.html'].replace('%display-error%', 'block').replace(
                '%error%', 'Esiste già una pizzeria con questo nome!')

        # Registra una nuova pizzeria e crea una sessione
        generated_uuid, expiring_date = self.generate_session()
        self.cookie = f"uuid={generated_uuid}"

        # Inserisce i dati della nuova pizzeria nel database
        DB.insert_pizzeria(name, owner_name)
        self.id = DB.get_pizzeria_from_name(name)["ID_pizzeria"]
        DB.insert_session(generated_uuid, self.id, 0, expiring_date)
        self.permission = 0

        # Reindirizza alla home con la registrazione completata
        self.redirect = "/"
        response, content = self.home()
        return 302, content.replace('%display-error%', 'none')

    def employee_login(self):
        # Restituisce la pagina HTML per il login dei dipendenti
        return 200, html_pages['static/employee-login.html'].replace('%display-error%', 'none')

    def employee_login_post(self):
        # Ottiene la lunghezza del contenuto della richiesta POST
        content_lenght = int(self.headers["Content-length"])
        
        # Legge i dati della richiesta e li analizza in una lista di coppie chiave-valore
        post_data = self.parse_entry_list(self.rfile.read(content_lenght).decode(), "&", "=")
        
        # Controlla se i campi 'id' e 'name' sono presenti nei dati inviati
        if not "id" in post_data or not "name" in post_data:
            # Ritorna una pagina di errore se mancano informazioni richieste
            return 200, html_pages['static/employee-login.html'].replace('%display-error%', 'block').replace('%error%', 'Inserisci sia il tuo codice che il nome della pizzeria!')
        
        # Ottiene il codice dipendente e il nome della pizzeria dai dati inviati
        employee_id = post_data['id'].replace("+", " ")
        name = post_data['name'].replace("+", " ")

        # Verifica che la pizzeria esista recuperando il suo ID dal database
        id_pizzeria = DB.get_pizzeria_from_name(name)
        if id_pizzeria is None:
            # Se la pizzeria non esiste, ritorna una pagina di errore
            return 200, html_pages['static/employee-login.html'].replace('%display-error%', 'block').replace('%error%', 'Codice personale o nome della pizzeria sbagliati!')
        
        # Estrae l'ID della pizzeria dal risultato
        id_pizzeria = id_pizzeria['ID_pizzeria']

        # Recupera tutti i dipendenti della pizzeria
        all_employees = DB.get_all_pizzeria_employees(id_pizzeria)

        # Se non ci sono dipendenti registrati, ritorna una pagina di errore
        if len(all_employees) == 0:
            return 200, html_pages['static/employee-login.html'].replace('%display-error%', 'block').replace('%error%', 'Codice personale o nome della pizzeria sbagliati!')

        # Recupera i dettagli del dipendente dal database utilizzando il codice fornito
        db_employee = DB.get_employee(employee_id)
        if db_employee is None:
            # Se il dipendente non esiste, ritorna una pagina di errore
            return 200, html_pages['static/employee-login.html'].replace('%display-error%', 'block').replace('%error%', 'Codice personale o nome della pizzeria sbagliati!')

        # Controlla se l'ID del dipendente è tra quelli associati alla pizzeria
        if int(employee_id) in all_employees:
            # Genera una nuova sessione e imposta il cookie
            generated_uuid, expiring_date = self.generate_session() 
            self.cookie = "uuid={}".format(generated_uuid)

            # Imposta l'ID e il permesso per l'utente
            self.id = employee_id
            DB.insert_session(generated_uuid, self.id, 1, expiring_date)
            self.permission = 1
            
            # Reindirizza alla homepage
            self.redirect = "/"
            response, content = self.home()
            return 302, content.replace('%display-error%', 'none')
        
        # Se l'ID del dipendente non è valido per questa pizzeria, ritorna una pagina di errore
        return 200, html_pages['static/employee-login.html'].replace('%display-error%', 'block').replace('%error%', 'Codice personale o nome della pizzeria sbagliati!')


    def shifts(self):
        # Controlla se l'utente è il proprietario della pizzeria (permesso 0)
        if self.permission == 0:
            # Verifica se nella richiesta GET è presente un timestamp
            if "timestamp" in self.get:
                # Converte il timestamp in oggetto datetime e genera la pagina dei turni
                timestamp = datetime.datetime.strptime(urlParser.unquote_plus(self.get['timestamp']), "%Y-%m-%d %H:%M:%S.%f")
                employees_page = SM.generate_html_shifts(self.id, timestamp=timestamp)
            else:
                # Genera la pagina dei turni senza timestamp specifico
                employees_page = SM.generate_html_shifts(self.id)
            return 200, employees_page
        elif self.permission == 1:
            # Se l'utente è un dipendente (permesso 1), genera la pagina dei turni per dipendenti
            return 200, SM.generate_html_employee_shifts(self.id)
        else:
            # Se i permessi sono invalidi, reindirizza alla pagina di login
            self.redirect = "/"
            return 302, html_pages['static/not-logged-home.html']


    def shifts_post(self):
        # Controlla se l'utente è il proprietario della pizzeria (permesso 0)
        if self.permission == 0:
            # Ottiene la lunghezza del contenuto della richiesta POST
            content_lenght = int(self.headers["Content-length"])
            # Decodifica i dati JSON inviati nel corpo della richiesta
            post_data = json.loads(self.rfile.read(content_lenght).decode())
            final_data = {}
            
            # Riorganizza i dati per associarli correttamente a turni e dipendenti
            for day_key, shifts in post_data.items():
                day = {}
                for shift, id_employee in shifts.items():
                    day[shift] = id_employee.split("#")[0]
                final_data[day_key] = day
            
            # Carica i turni nel database
            DB.upload_shift(final_data, self.id)
            
            # Genera la pagina aggiornata dei turni
            home_page: str = html_pages['static/home.html']
            home_page = home_page.replace("%content%", SM.generate_html_shifts(self.id))
            return 200, home_page
        elif self.permission == 1:
            # Se l'utente è un dipendente, mostra che l'operazione non è ancora implementata
            return 200, "employee shifts post not implemented yet"
        

    def employees(self):
        # Controlla se l'utente è il proprietario della pizzeria (permesso 0)
        if self.permission == 0:
            # Genera e ritorna la pagina HTML con l'elenco dei dipendenti
            employees_page = EM.generate_html_employees(self.id)
            return 200, employees_page
        else:
            # Se l'utente non ha il permesso richiesto, ritorna una pagina di errore 404
            return 404, html_pages['static/404.html']
        
    def add_employee(self):
        # Controlla se l'utente è il proprietario della pizzeria (permesso 0)
        if self.permission == 0:
            # Ottiene la lunghezza del contenuto della richiesta POST
            content_lenght = int(self.headers["Content-length"])
            # Decodifica i dati JSON inviati nel corpo della richiesta
            post_data = json.loads(self.rfile.read(content_lenght).decode())
            
            # Verifica che i dati obbligatori (nome, cognome, data di nascita) siano presenti
            if "name" in post_data and "surname" in post_data and "birthdate" in post_data:
                # Converte la data di nascita da stringa a oggetto datetime
                birthdate = datetime.datetime.strptime(post_data["birthdate"], "%Y-%m-%d")
                # Inserisce il nuovo dipendente nel database
                DB.insert_employee(self.id, post_data["name"], post_data["surname"], birthdate)
                # Ritorna la pagina aggiornata con l'elenco dei dipendenti
                return 200, self.employees()[1]
            else:
                # Se i dati sono mancanti o errati, stampa un messaggio di errore e ritorna l'elenco
                print("Wrong add employee post data format!")
                return 200, self.employees()[1]  # TODO: Aggiungere un messaggio di errore visibile
        else:
            # Se l'utente non ha il permesso richiesto, ritorna una pagina di errore 404
            return 404, html_pages['static/404.html']


    def modify_employee(self):
        # Controlla se l'utente è il proprietario della pizzeria (permesso 0)
        if self.permission == 0:
            # Ottiene la lunghezza del contenuto della richiesta POST
            content_lenght = int(self.headers["Content-length"])
            # Decodifica i dati JSON inviati nel corpo della richiesta
            post_data = json.loads(self.rfile.read(content_lenght).decode())
            
            # Verifica che tutti i campi obbligatori siano presenti
            if "name" in post_data and "surname" in post_data and "birthdate" in post_data and "id" in post_data:
                # Converte la data di nascita da stringa a oggetto datetime
                birthdate = datetime.datetime.strptime(post_data["birthdate"], "%Y-%m-%d")
                # Aggiorna i dati del dipendente nel database
                DB.update_employee(int(post_data["id"]), self.id, post_data["name"], post_data["surname"], birthdate)
                # Ritorna la funzione `employees` per aggiornare l'elenco
                return 200, self.employees()[1]
            else:
                # Se i dati sono mancanti o errati, stampa un messaggio di errore e ritorna l'elenco
                print("Wrong add employee post data format!")
                return 200, self.employees()[1]
        else:
            # Se l'utente non ha il permesso richiesto, ritorna una pagina di errore 404
            return 404, html_pages['static/404.html']


    def delete_employee(self):
        # Controlla se l'utente è il proprietario della pizzeria (permesso 0)
        if self.permission == 0:
            # Ottiene la lunghezza del contenuto della richiesta POST
            content_lenght = int(self.headers["Content-length"])
            # Legge e decodifica il dato inviato (ID del dipendente da eliminare)
            post_data = self.rfile.read(content_lenght).decode()
            
            # Se il dato non è nullo, elimina il dipendente dal database
            if post_data is not None:
                DB.delete_employee(int(post_data))
            else:
                # Se il dato è nullo, stampa un messaggio di errore
                print("Wrong add employee post data format!")
            # Ritorna la funzione `employees` per aggiornare l'elenco
            return 200, self.employees()[1]
        else:
            # Se l'utente non ha il permesso richiesto, ritorna una pagina di errore 404
            return 404, html_pages['static/404.html']

    def requests(self):
        # Controlla se l'utente è un dipendente (permesso 1)
        if self.permission == 1:
            # Genera e ritorna la pagina HTML con le richieste
            requests_page = RM.get_html_requests(self.id)
            return 200, requests_page
        else:
            # Se l'utente non ha il permesso richiesto, ritorna una pagina di errore 404
            return 404, html_pages['static/404.html']


    def make_request(self):
        # Controlla se l'utente è un dipendente (permesso 1)
        if self.permission == 1:
            # Ottiene la lunghezza del contenuto della richiesta POST
            content_lenght = int(self.headers["Content-length"])
            # Decodifica i dati JSON inviati nel corpo della richiesta
            post_data = json.loads(self.rfile.read(content_lenght).decode())
            
            # Estrae i dettagli della richiesta dallo JSON
            questioner_id = int(post_data['questioner_id'])
            questioner_day_id = int(post_data['questioner_day_id'])
            questioner_index = int(post_data['questioner_index'])
            questioned_id = int(post_data['questioned_id'])
            questioned_day_id = int(post_data['questioned_day_id'])
            questioned_index = int(post_data['questioned_index'])
            
            # Recupera l'ID della pizzeria associata all'utente
            employee = DB.get_employee(self.id)
            id_pizzeria = employee['id_pizzeria']
            
            # Inserisce la richiesta nel database
            DB.insert_request(id_pizzeria, questioner_id, questioner_day_id, questioner_index, questioned_id, questioned_day_id, questioned_index)
            
            # Ritorna la pagina aggiornata con i turni dei dipendenti
            return 200, SM.generate_html_employee_shifts(self.id)
        else:
            # Se l'utente non ha il permesso richiesto, ritorna una pagina di errore 404
            return 404, html_pages['static/404.html']

            
    def accept_request(self):
        # Controlla se l'utente è un dipendente (permesso 1)
        if self.permission == 1:
            # Ottiene la lunghezza del contenuto della richiesta POST
            content_lenght = int(self.headers["Content-length"])
            # Legge e decodifica i dati inviati nel corpo della richiesta (ID della richiesta da accettare)
            post_data = self.rfile.read(content_lenght).decode()
            
            # Se il dato non è nullo, accetta la richiesta nel database
            if post_data is not None:
                RM.accept_request(int(post_data))
                # Genera e ritorna la pagina aggiornata delle richieste
                requests_page = RM.get_html_requests(self.id)
                # Imposta un reindirizzamento alla pagina delle richieste
                self.redirect = '/requests'
                return 302, requests_page
        else:
            # Se l'utente non ha il permesso richiesto, ritorna una pagina di errore 404
            return 404, html_pages['static/404.html']

        
    def decline_request(self):
        # Controlla se l'utente è un dipendente (permesso 1)
        if self.permission == 1:
            # Ottiene la lunghezza del contenuto della richiesta POST
            content_lenght = int(self.headers["Content-length"])
            # Legge e decodifica i dati inviati nel corpo della richiesta (ID della richiesta da declinare)
            post_data = self.rfile.read(content_lenght).decode()
            
            # Se il dato non è nullo, elimina la richiesta dal database
            if post_data is not None:
                DB.delete_request(int(post_data))
                # Genera e ritorna la pagina aggiornata delle richieste
                requests_page = RM.get_html_requests(self.id)
                return 200, requests_page
        else:
            # Se l'utente non ha il permesso richiesto, ritorna una pagina di errore 404
            return 404, html_pages['static/404.html']

    
    def home(self):
        # Verifica i permessi dell'utente per personalizzare la pagina della home
        if self.permission == 0:
            # Utente con permessi amministrativi (proprietario della pizzeria)
            return 200, (html_pages['template/main-page.html']
                        .replace("%content%", html_pages['template/home.html'])  # Inserisce il contenuto della home
                        .replace("%title%", "Home")  # Imposta il titolo della pagina
                        .replace("%style-path%", "new-home-style.css")  # Imposta il file CSS
                        .replace("%home-active%", "active")  # Evidenzia la voce 'home' nel menu
                        .replace("%shifts-active%", "")  # Disattiva l'evidenziazione della voce 'turni'
                        .replace("%employees-active%", "")  # Disattiva l'evidenziazione della voce 'dipendenti'
                        .replace("%pizzeria-name%", DB.get_pizzeria(self.id)["name"]))  # Inserisce il nome della pizzeria
        elif self.permission == 1:
            # Utente con permessi di dipendente
            employee = DB.get_employee(self.id)  # Recupera i dati del dipendente
            pizzeria = DB.get_pizzeria(employee['id_pizzeria'])  # Recupera i dati della pizzeria
            return 200, (html_pages['template/employee-main-page.html']
                        .replace("%content%", html_pages['template/employee-home.html'])  # Inserisce il contenuto della home dipendente
                        .replace("%title%", "Home")  # Imposta il titolo della pagina
                        .replace("%style-path%", "new-home-style.css")  # Imposta il file CSS
                        .replace("%home-active%", "active")  # Evidenzia la voce 'home' nel menu
                        .replace("%shifts-active%", "")  # Disattiva l'evidenziazione della voce 'turni'
                        .replace("%employees-active%", "")  # Disattiva l'evidenziazione della voce 'dipendenti'
                        .replace("%pizzeria-name%", pizzeria['name']))  # Inserisce il nome della pizzeria
        else:
            # Se l'utente non ha permessi validi, restituisce una pagina 404
            return 404, html_pages['static/404.html']


    def download_pdf(self):
        id_pizzeria = None
        if self.permission == 0:
            id_pizzeria = self.id
        elif self.permission == 1:
            employee = DB.get_employee(self.id)
            id_pizzeria = employee['id_pizzeria']
            
        if id_pizzeria is not None:
            if "timestamp" in self.get:
                timestamp = datetime.datetime.strptime(urlParser.unquote_plus(self.get['timestamp']), "%Y-%m-%d %H:%M:%S.%f")
                buffer = SM.create_shift_pdf(id_pizzeria, timestamp)
                return buffer, 'application/pdf', 'report_turni.pdf'
            else:
                timestamps = DB.get_all_pizzeria_timestamps(id_pizzeria)
        
                if len(timestamps) == 0:
                    return None, None, None
                buffer = SM.create_shift_pdf(id_pizzeria, timestamps[0])
                return buffer, 'application/pdf', 'report_turni.pdf'
        else:
            return None
            
    def download_img(self):
        id_pizzeria = None
        if self.permission == 0:
            id_pizzeria = self.id
        elif self.permission == 1:
            employee = DB.get_employee(self.id)
            id_pizzeria = employee['id_pizzeria']
            
        if id_pizzeria is not None:
            if "timestamp" in self.get:
                timestamp = datetime.datetime.strptime(urlParser.unquote_plus(self.get['timestamp']), "%Y-%m-%d %H:%M:%S.%f")
                buffer = SM.create_shift_image(id_pizzeria, timestamp)
                return buffer, 'image/png', 'report_turni.png'
            else:
                timestamps = DB.get_all_pizzeria_timestamps(id_pizzeria)
        
                if len(timestamps) == 0:
                    return None, None, None
                buffer = SM.create_shift_image(id_pizzeria, timestamps[0])
                return buffer, 'image/png', 'report_turni.png'
        else:
            return None

    def generate_uuid(self):
        # Genera un UUID univoco utilizzando la libreria uuid
        return str(uuid.uuid4())
    
    def generate_session(self):
        # Genera un UUID per identificare la sessione
        generated_uuid = self.generate_uuid()
        
        # Ottiene la data e ora corrente
        now = datetime.datetime.now()
        
        # Calcola il numero di giorni totali da aggiungere considerando giorno, mese e anno
        day_add = expiring_day_add
        day_add += expiring_month_add * 30
        day_add += expiring_year_add * 365

        # Calcola la data di scadenza aggiungendo giorni, ore e minuti alla data attuale
        expiring_date = now + datetime.timedelta(days=day_add, 
                                                hours=expiring_hour_add,
                                                minutes=expiring_minute_add)
        # Restituisce l'UUID generato e la data di scadenza
        return generated_uuid, expiring_date


    def get_session(self, cookies: dict) -> bool:
        # Controlla se il cookie 'uuid' è presente
        if "uuid" not in cookies:
            return False, False
        
        # Recupera la sessione dal database utilizzando l'UUID
        db_session = DB.get_session_from_uuid(cookies['uuid'])
        if db_session is None:
            # Restituisce False se non esiste una sessione corrispondente
            return False, False
        
        # Restituisce la chiave e il valore della sessione recuperata
        for key in db_session.keys():
            return key, db_session[key]

            

    def parse_entry_list(self, entrys: str, entry_separator: str, key_value_separator: str) -> dict:
        # Verifica se l'input è nullo o vuoto
        if entrys is None or entrys == "":
            return {}
        
        # Inizializza un dizionario vuoto per contenere le coppie chiave-valore
        entry_dict = {}
        # Divide l'input in una lista utilizzando il separatore delle voci
        entry_list = map(str.strip, entrys.split(entry_separator))
        for entry in entry_list:
            if entry != "":
                # Divide ogni voce in chiave e valore utilizzando il separatore chiave-valore
                key, value = entry.split(key_value_separator)
                entry_dict[key] = value
        
        # Restituisce il dizionario risultante
        return entry_dict


def init(passed_hostname: str, passed_server_port: int, passed_html_pages: dict, passed_css_files: dict, passed_js_files: dict, passed_immages: dict):
    # Inizializza variabili globali con i valori passati come argomenti
    global server_port, hostname, html_pages, css_files, js_files, immages, web_server
    html_pages = passed_html_pages
    css_files = passed_css_files
    js_files = passed_js_files
    immages = passed_immages

    hostname = passed_hostname
    server_port = passed_server_port

    # Crea un server HTTP con l'handler specificato
    web_server = HTTPServer((hostname, server_port), Server_handler)

def start():
    try:
        # Avvia il server web in modalità di ascolto continuo
        web_server.serve_forever()
    except KeyboardInterrupt:
        # Interrompe l'esecuzione se viene premuto Ctrl+C
        pass

def shutdown():
    global web_server
    # Chiude il server web
    web_server.server_close()
import WebServer as WS
import DatabaseManager as DB
import ShiftsManager as SM
import EmployeesManager as EM
import RequestsManager as RM
import Logger
import os

def get_all_files(path = "static"):
    html_pages = {}
    css_files = {}
    js_files = {}
    images = {}

    if not os.path.isdir(path):
        return "not a directory"
    
    for file_name in os.listdir(path):
        if os.path.isdir(path + "/" + file_name):
            new_html_pages, new_css_files, new_js_files, new_images = get_all_files(path=path + "/" + file_name)
            html_pages.update(new_html_pages)
            css_files.update(new_css_files)
            js_files.update(new_js_files)
            images.update(new_images)
        elif file_name.endswith(".html"):
           with open(path + "/" + file_name) as f:
                html_pages[path + "/" + file_name] = f.read()
        elif file_name.endswith(".css"):
           with open(path + "/" + file_name) as f:
                css_files[path + "/" + file_name] = f.read()
        elif file_name.endswith(".js"):
           with open(path + "/" + file_name) as f:
                js_files[path + "/" + file_name] = f.read()
        elif file_name.endswith(".jpeg"):
           with open(path + "/" + file_name, "rb") as f:
                images[path + "/" + file_name] = f.read()
        elif file_name.endswith(".png"):
           with open(path + "/" + file_name, "rb") as f:
                images[path + "/" + file_name] = f.read()
        elif file_name.endswith(".jpg"):
           with open(path + "/" + file_name, "rb") as f:
                images[path + "/" + file_name] = f.read()
        elif file_name.endswith(".ico"):
           with open(path + "/" + file_name, "rb") as f:
                images[path + "/" + file_name] = f.read()
        elif file_name.endswith(".webp"):
           with open(path + "/" + file_name, "rb") as f:
                images[path + "/" + file_name] = f.read()

    return html_pages, css_files, js_files, images

def main():
    hostname = "192.168.1.70"
    server_port = 80


    Logger.log("Starting DB...")
    DB.init()
    Logger.log("DB started correctly")

    Logger.log("Trying load all html pages...")
    html_pages, css_files, js_files, immages =  get_all_files()
    new_html_pages, new_css_files, new_js_files, new_immages =  get_all_files(path="template")
    html_pages.update(new_html_pages)
    css_files.update(new_css_files)
    js_files.update(new_js_files)
    immages.update(new_immages)
    Logger.log("All html pages loaded correctly")

    Logger.log("Tring initializing Employees Manager...")
    EM.init()
    Logger.log("Employees Manager initialized correctly")

    Logger.log("Tring initializing Shifts Manager...")
    SM.init()
    Logger.log("Shifts Manager initialized correctly")
    
    Logger.log("Tring initializing Requests Manager...")
    RM.init()
    Logger.log("Requests Manager initialized correctly")

    Logger.log("Trying initializing server...")
    WS.init(hostname, server_port, html_pages, css_files, js_files, immages)
    Logger.log("Server startinitialized correctly")

    Logger.log("Starting server...")
    WS.start()


    Logger.log("Stopping server...")
    WS.shutdown()
    Logger.log("Server stopped")

    Logger.log("Closing DB...")
    DB.close()
    Logger.log("DB closed correctly")

if __name__ == "__main__":
    main()
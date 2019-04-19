import socketserver
import http.server
import termcolor
import json

PORT = 8000
HOSTNAME = "rest.ensembl.org"
METHOD = "GET"
content = ""

socketserver.TCPServer.allow_reuse_address = True

headers = {'User-Agent': 'http-client'}

def get_json(ENDPOINT):
    conn = http.client.HTTPSConnection(HOSTNAME)
    conn.request(METHOD, ENDPOINT, None, headers)
    r1 = conn.getresponse()
    print()
    print("Response received: ", end='')
    print(r1.status, r1.reason)

    text_json = r1.read().decode("utf-8")
    conn.close()
    json_info = json.loads(text_json)

    return json_info

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path

        termcolor.cprint("GET Received", "green")
        termcolor.cprint("Request line: {}".format(self.requestline), "cyan")
        print("     Cnd: {}".format(self.command))
        termcolor.cprint("Path:  {}  ".format(path), "yellow")
        print()

        if path == "/":
            with open("index.html", "r") as f:
                content = f.read()

        elif "listSpecies" in path:
            json_species = list()

            for i in get_json("/info/species?content-type=application/json")["species"]:
                json_species.append(i)

            species_list = list()

            for i in range(len(json_species)):
                species_list.append(json_species[i]["display_name"])

            print(species_list)
            print(len(species_list))

            if "limit" in path:
                limit = path[path.find("=") + 1:]

                if limit == "":
                    header_inf = "List of species:\n"
                    photo = "https://i.imgur.com/wHk5lIk.jpg"
                    data = str()

                    for i in range(len(species_list)):
                        data += str(i + 1) + ". " + str(species_list[i]) + " | " + "\n"

                else:
                    if limit.isalpha():
                        header_inf = "Invalid limit parameter. Please, try again with a number from 1 to {}".format(str(len(species_list)))
                        data = ""
                        photo = "https://i.imgur.com/poj7xfa.jpg"

                    else:
                        limit = int(limit)

                        if limit > len(json_species):
                            header_inf = "Sorry, there are not that many species in the database"
                            data = "Please, choose a number from 1 to {}.".format(str(len(species_list)))
                            photo = "https://i.imgur.com/poj7xfa.jpg"

                        elif limit <= 0:
                            header_inf = "Invalid limit parameter. Please, try again with a number from 1 to {}.".format(str(len(species_list)))
                            data = ""
                            photo = "https://i.imgur.com/poj7xfa.jpg"

                        else:
                            header_inf = "Showing {} species.".format(str(limit))
                            data = str(" ")
                            photo = "https://i.imgur.com/wHk5lIk.jpg"

                            for i in range(limit):
                                data += str(i + 1) + ". " + str(species_list[i]) + " | " + "\n"

                        termcolor.cprint("Limit is {}".format(limit), "green")


                with open("listSpecies.html", "r") as file:
                    content = file.read().replace("SPECIESIMAGE", photo).replace("SPECIESHEADER", header_inf).replace("SPECIESDATA", data)
                    file.close()

        elif "karyotype" in path:
            specie_input = path[path.find("=") + 1:].lower()
            print(specie_input)
            karyo = get_json("/info/assembly/" + specie_input + "?content-type=application/json")
            print(karyo)
            specie = specie_input.replace("+", " ")
            data = ""

            if "karyotype" in karyo:
                karyotype = karyo["karyotype"]
                photo = "https://i.imgur.com/mXVUQAW.jpg"

                for i in range(len(karyotype)):
                    data += karyotype[i] + " | " + " "

                data = "Showing karyotype: " + data

            else:
                data = "Sorry, the specie '{}' is not available in the database.".format(specie)
                photo = "https://i.imgur.com/L6IgO0M.jpg"

            with open("karyotype.html", "r") as file:
                content = file.read().replace("KARYOIMAGE", photo).replace("KARYOHEADER", str("Input specie: {}.".format(specie))).replace("KARYODATA", data)
                file.close()

        else:
            with open("error.html", "r") as file:
                content = file.read()
                file.close()

        self.send_response(200)

        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(str.encode(content)))

        self.end_headers()

        self.wfile.write(str.encode(content))

Handler = TestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:

    print("Serving at PORT", PORT)

    try:
        httpd.serve_forever()

    except KeyboardInterrupt:
        print("")
        print("Stopped by the user")
        httpd.server_close()

print("")
print("Server Stopped")
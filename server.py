import socketserver
import http.server
import termcolor
import json
from Seq import Seq

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
    print(ENDPOINT)
    print()
    print("Response received: ", end='')
    print(r1.status, r1.reason)

    text_json = r1.read().decode("utf-8")
    conn.close()
    json_info = json.loads(text_json)

    print('Json retrieved', json_info)
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

            if "limit" in path:
                limit = path[path.find("=") + 1:]

                if limit == "":
                    header_inf = "List of species: "
                    photo = "https://i.imgur.com/RMjXpq5.jpg"
                    data = list()

                    for i in range(len(species_list)):
                        data.append(str(i + 1) + ". " + str(species_list[i]))

                else:
                    try:
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
                            data = list()
                            photo = "https://i.imgur.com/wHk5lIk.jpg"

                            for i in range(limit):
                                data.append(str(i + 1) + ". " + str(species_list[i]))


                        termcolor.cprint("Limit is {}".format(limit), "green")

                    except ValueError:
                        header_inf = "Invalid limit parameter. Please, try again with a number from 1 to {}.".format(str(len(species_list)))
                        data = ""
                        photo = "https://i.imgur.com/aKaXdU6.jpg"

                data = str(data).strip("[]").replace("'", "")

                print("List of species from the .json file: ", species_list)
                print("Lenght of the list: ", len(species_list))
                print("Informative text to the user sent ro the server: ", header_inf)
                print("Data sent to the server: ", data)

                with open("listSpecies.html", "r") as file:
                    content = file.read().replace("SPECIESIMAGE", photo).replace("SPECIESHEADER", header_inf).replace("SPECIESDATA", data)
                    file.close()

        elif "karyotype" in path:
            specie_input = path[path.find("=") + 1:].lower().replace("+", "_").replace("/", "").lower()
            karyo = get_json("/info/assembly/" + specie_input + "?content-type=application/json")
            specie = specie_input.replace("_", " ")
            data = list()

            if not specie.replace(" ", "").isalpha():
                data = "I'm sorry to tell you that '{}' is not a specie. Try again.".format(specie)
                photo = "https://i.imgur.com/aKaXdU6.jpg"

            else:
                try:
                    karyotype = karyo["karyotype"]

                    if karyo["karyotype"] == []:
                        data = "Karyotype not available in the database."
                        photo = "https://i.imgur.com/poj7xfa.jpg"


                    else:
                        for i in range(len(karyotype)):
                            data.append(karyotype[i])

                    data = "Showing karyotype: {}".format(str(data).strip("[]").replace("'", ""))
                    photo = "https://i.imgur.com/ihzq1ZU.jpg"


                except KeyError:
                    data = "Sorry, the specie '{}' is not available in the database.".format(specie.replace("_", " "))
                    photo = "https://i.imgur.com/poj7xfa.jpg"

            print("Specie input: ", specie_input)
            print("Json retrieved from the ENSEMBL webpage: ", karyo)
            print("Data sent to the server: ", data)
            print()

            with open("karyotype.html", "r") as file:
                content = file.read().replace("KARYOIMAGE", photo).replace("KARYOHEADER", str("Input specie: {}.".format(specie))).replace("KARYODATA", data)
                file.close()

        elif "chromosomeLength" in path:
            specie = path[path.find("specie=") + 7:path.find("&")].lower().replace("+", "_").replace("/", "").lower()
            karyo = get_json("/info/assembly/" + specie + "?content-type=application/json")

            try:
                json_karyo = karyo["karyotype"]
                karyotype = karyo["top_level_region"]

                print("Karyotype is", karyotype)

                num = path[path.find("chromo=") + 7:]
                print(num, type(num))

                if num.isalpha():
                    num = str(num.upper())

                    for i in karyotype:
                        print(i["name"])

                        if num == i["name"]:
                            length = i["length"]
                            break

                        else:
                            length = 'error'

                    if length == "error":
                        data = "I'm sorry to tell you that '{}' is not a valid input chromosome. Check the 'Karyotype' page to know them".format(num)
                        photo = "https://i.imgur.com/aKaXdU6.jpg"

                    else:
                        data = "Length of chromosome '{}' of the specie '{}' is {} bp.".format(num, specie.replace("_", " "), str(length))
                        photo = "https://i.imgur.com/RuuZ4VG.jpg"

                elif num.isdigit():
                    if len(json_karyo) >= int(num):
                        for e in karyotype:
                            if num == e['name']:
                                length = e['length']
                                break

                        data = "Length of chromosome '{}' of the specie '{}' is {} bp.".format(num, specie.replace("_", " "), str(length))
                        photo = "https://i.imgur.com/RuuZ4VG.jpg"

                    elif len(json_karyo)< int(num):
                        data = "Chromosome not found. There are {} chromosomes available. Check the 'Karyotype' page to know them".format(str(len(json_karyo)))
                        photo = "https://i.imgur.com/poj7xfa.jpg"

                else:
                    for e in num:
                        if e.isalpha():
                            num = num.replace(e, e.upper())

                    print(num)

                    for i in karyotype:
                        print(i["name"])

                        if num == i["name"]:
                            length = i["length"]
                            break

                        else:
                            length = 'error'

                    if length == "error":
                        data = "Chromosome not found. There are {} chromosomes available. Check the 'Karyotype' page to know them".format(str(len(json_karyo)))
                        photo = "https://i.imgur.com/aKaXdU6.jpg"

                    else:
                        data = "Length of chromosome '{}' of the specie '{}' is {} bp.".format(num, specie.replace("_", " "), str(length))
                        photo = "https://i.imgur.com/RuuZ4VG.jpg"


            except KeyError:
                data= "Karyotype for '{}' is not available.".format(specie.replace("_", " "))
                photo = "https://i.imgur.com/poj7xfa.jpg"

            with open("chromlength.html", "r") as file:
                content = file.read().replace("LENIMAGE", photo).replace("LENHEADER", str(data))
                file.close()

        elif "geneSeq" in path:
            gene_input = path[path.find("gene=") + 5:].upper()
            print(gene_input)

            try:
                gene_id = get_json("/lookup/symbol/homo_sapiens/" + gene_input + "?expand=1;content-type=application/json")["id"]
                print(gene_id)
                gene_seq = get_json("/sequence/id/" + gene_id + "?content-type=application/json")["seq"]
                print(gene_seq)

                header = "The sequence for '{}' is: ".format(gene_input)
                data = gene_seq
                photo = "https://i.imgur.com/Fhayqk0.jpg"

            except KeyError:
                header = ""
                data = "Sorry, the gene '{}' was not found for Homo Sapiens specie.".format(gene_input)
                photo = "https://i.imgur.com/aKaXdU6.jpg"

            with open("gene.html", "r") as file:
                content = file.read().replace("GENEOPERAT", "GENE SEQUENCE").replace("SEQIMAGE", photo).replace("SEQHEADER", header).replace("SEQDATA", data)
                file.close()

        elif "geneInfo" in path:
            gene_input = path[path.find("gene=") + 5:].upper()

            try:
                gene = get_json("/lookup/symbol/homo_sapiens/" + gene_input + "?expand=1;content-type=application/json")
                gene_id = gene["id"]
                gene_start= gene["start"]
                gene_end = gene["end"]
                gen_chromo = gene["seq_region_name"]
                lenght = len(get_json("/sequence/id/" + gene_id + "?content-type=application/json")["seq"])

                header = "Information for gene '{}' is: ".format(gene_input)
                data = "<br>Gene ID: {}</br><br>Start: {}</br><br>End: {}</br><br>Lenght: {}</br><br>Chromosome where it belongs: {}</br>".format(gene_id, gene_start, gene_end, lenght, gen_chromo)
                photo = "https://i.imgur.com/Fhayqk0.jpg"

            except KeyError:
                header = ""
                data = "Sorry, the gene '{}' was not found for Homo Sapiens specie.".format(gene_input)
                photo = "https://i.imgur.com/poj7xfa.jpg"

            with open("gene.html", "r") as file:
                content = file.read().replace("GENEOPERAT", "GENE INFORMATION").replace("SEQIMAGE", photo).replace("SEQHEADER", header).replace("SEQDATA", data)
                file.close()

        elif "geneCalc" in path:
            gene_input = path[path.find("gene=") + 5:].upper()

            try:
                gene_id = get_json("/lookup/symbol/homo_sapiens/" + gene_input + "?expand=1;content-type=application/json")["id"]
                sequence = Seq(get_json("/sequence/id/" + gene_id + "?content-type=application/json")["seq"])

                lenght = sequence.len()
                percA = sequence.perc("A")
                percC = sequence.perc("C")
                percG = sequence.perc("G")
                percT = sequence.perc("T")

                header = "Information for gene '{}' is: ".format(gene_input)
                data = "<br>Lenght: {}</br><br>Percentage of Adenine: {}</br><br>Percentage of Thymine: {}</br><br>Percentage of Cytosine: {}</br><br>Percentage of Guanine: {}</br>".format(lenght, percA, percT, percC, percG)
                photo = "https://i.imgur.com/Fhayqk0.jpg"

            except KeyError:
                header = ""
                data = "Sorry, the gene '{}' was not found for Homo Sapiens specie.".format(gene_input)
                photo = "https://i.imgur.com/aKaXdU6.jpg"

            with open("gene.html", "r") as file:
                content = file.read().replace("GENEOPERAT", "GENE OPERATIONS").replace("SEQIMAGE", photo).replace("SEQHEADER", header).replace("SEQDATA", data)
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
        print("Server stopped.")
        httpd.server_close()

print("")
print("Server Stopped")
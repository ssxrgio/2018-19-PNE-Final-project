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

    print('Json retrieved:', json_info)

    return json_info

def dict_species(limit, list_1, list_2):
    try:
        json_dict = dict()

        if limit > len(list_1):
            json_dict = {"error" : "there are not that many species in the database. Please, choose a number from 1 to {}.".format(str(len(list_1)))}

        elif limit <= 0:
            json_dict = {"error" : "invalid limit parameter. Please, try again with a number from 1 to {}.".format(str(len(list_1)))}

        else:
            for i in range(limit):
                json_dict["specie {}".format(str(i+1))] = {
                    "name" : list_1[i], "binomial name" : list_2[i]
                }

    except TypeError:
        json_dict = {"error": "invalid limit parameter. Please, try again with a number from 1 to {}.".format(str(len(list_1)))}

    return json_dict

def dict_karyotype(limit, specie, data):
    if limit == 'key':
        json_dict = {"error": "specie '{}' is not available in the database.".format(specie.replace("_", " "))}

    elif limit == 'value':
        json_dict = {"error" : "'{}' is not a specie. Try again.".format(specie)}

    else:
        json_dict = dict()

        for i in range(limit):
            json_dict["karyotype for {}".format(specie)] = data

    return json_dict

def dict_length(chromo, specie, length):
    if chromo == "key":
        json_dict = {"error": "chromosome not found"}

    elif chromo == "specie":
        json_dict = {"error": "karyotype for {} is not available.".format(specie)}

    else:
        json_dict = {"length of chromosome {} for {}".format(chromo, specie): length}

    return json_dict

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        global json_data
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
            name_species_list = list()

            for i in range(len(json_species)):
                species_list.append(json_species[i]["display_name"])
                name_species_list.append(json_species[i]["name"])

            if "limit" in path:

                if "&json=1" in path:
                    limit = path[path.find("=") + 1:path.find("&")]
                    print(limit)

                else:
                    limit = path[path.find("=") + 1:]

                if limit == "":
                    limit = len(species_list)
                    header_inf = "List of species: "
                    photo = "https://i.imgur.com/RMjXpq5.jpg"
                    data = list()

                    for i in range(len(species_list)):
                        data.append("<li style=\"font-family:helvetica;font-size:90%;word-break:break-all\"><p style=\"font-weight:bold\">{}.</p> Binomial name: {}</li>".format(str(species_list[i]), str(name_species_list[i]).capitalize().replace("_", " ")))

                    data = "<ol>{}</ol>".format(str(data).strip("[]").replace("'", "").replace(",", ""))

                else:
                    try:
                        limit = int(limit)

                        if limit > len(json_species):
                            header_inf = "Sorry, there are not that many species in the database"
                            data = "Please, choose a number from 1 to {}.".format(str(len(species_list)))
                            photo = "https://i.imgur.com/poj7xfa.jpg"

                        elif limit <= 0:
                            header_inf = "Error: Invalid limit parameter. Please, try again with a number from 1 to {}.".format(str(len(species_list)))
                            data = ""
                            photo = "https://i.imgur.com/poj7xfa.jpg"

                        else:
                            header_inf = "Showing {} species.".format(str(limit))
                            data = list()
                            photo = "https://i.imgur.com/wHk5lIk.jpg"

                            for i in range(limit):
                                data.append("<li style=\"font-family:helvetica;font-size:90%;word-break:break-all\"><p style=\"font-weight:bold\">{}.</p> Binomial name: {}</li>".format(str(species_list[i]), str(name_species_list[i]).capitalize().replace("_", " ")))

                            data = "<ol>{}</ol>".format(str(data).strip("[]").replace("'", "").replace(",", ""))

                    except ValueError:
                        header_inf = "Error: invalid limit parameter. Please, try again with a number from 1 to {}.".format(str(len(species_list)))
                        data = ""
                        photo = "https://i.imgur.com/aKaXdU6.jpg"

            else:
                limit = len(species_list)
                header_inf = "List of species: "
                photo = "https://i.imgur.com/RMjXpq5.jpg"
                data = list()

                for i in range(len(species_list)):
                    data.append("<li style=\"font-family:helvetica;font-size:90%;word-break:break-all\"><p style=\"font-weight:bold\">{}.</p> Binomial name: {}</li>".format(str(species_list[i]), str(name_species_list[i]).capitalize().replace("_", " ")))

                data = "<ol>{}</ol>".format(str(data).strip("[]").replace("'", "").replace(",", ""))

            data = str(data).strip("[]").replace("'", "")

            json_data = dict_species(limit, species_list, name_species_list)

            with open("results.html", "r") as file:
                content = file.read().replace("OPERATION", "LIST OF SPECIES").replace("IMAGE", photo).replace("HEADER", header_inf).replace("DATA", data).replace("COLOURCARD", "#6da4f9")
                file.close()

        elif "karyotype" in path:

            if "&json=1" in path:
                specie_input = path[path.find("=") + 1:path.find("&")].lower().replace("+", "_").replace("/", "").lower()

            else:
                specie_input = path[path.find("=") + 1:].lower().replace("+", "_").replace("/", "").lower()

            karyo = get_json("/info/assembly/" + specie_input + "?content-type=application/json")
            specie = specie_input.replace("_", " ")
            data_list = list()

            try:
                try:
                    karyotype = karyo["karyotype"]

                    if karyo["karyotype"] == []:
                        data = "Karyotype not available in the database."
                        photo = "https://i.imgur.com/poj7xfa.jpg"

                    else:
                        for i in range(len(karyotype)):
                            data_list.append(karyotype[i])

                        data = "Showing karyotype: {}".format(str(data_list).strip("[]").replace("'", ""))
                        photo = "https://i.imgur.com/ihzq1ZU.jpg"

                    DATA = None
                    LIMIT = "key"

                except KeyError:
                    data = "Error: specie '{}' is not available in the database.".format(specie.replace("_", " "))
                    photo = "https://i.imgur.com/poj7xfa.jpg"

                    DATA = None
                    LIMIT = "key"

            except ValueError:
                data = "Error: '{}' is not a specie. Try again.".format(specie)
                photo = "https://i.imgur.com/aKaXdU6.jpg"

                DATA = None
                LIMIT = "value"

            json_data = dict_karyotype(LIMIT, specie, DATA)

            with open("results.html", "r") as file:
                content = file.read().replace("OPERATION", "KARYOTYPE").replace("IMAGE", photo).replace("HEADER", str("Input specie: {}.".format(specie))).replace("DATA", data).replace("COLOURCARD", "#B7EC77")
                file.close()

        elif "chromosomeLength" in path:
            specie = path[path.find("specie=") + 7:path.find("&")].lower().replace("+", "_").replace("/", "").lower()
            karyo = get_json("/info/assembly/" + specie + "?content-type=application/json")

            try:
                json_karyo = karyo["karyotype"]
                karyotype = karyo["top_level_region"]

                if "&json=1" in path:
                    num = path[path.find("chromo=") + 7: path.find("&json=1")]

                else:
                    num = path[path.find("chromo=") + 7:]

                print(num, type(num))

                if num.isalpha():
                    num = str(num.upper())

                    for i in karyotype:
                        if num == i["name"]:
                            length = i["length"]
                            break

                        else:
                            length = 'error'

                    if length == "error":
                        data = "Error '{}' is not a valid input chromosome. Check the 'Karyotype' page to know them".format(num)
                        photo = "https://i.imgur.com/aKaXdU6.jpg"

                        NUM = "key"
                        LENGTH = None


                    else:
                        data = "Length of chromosome '{}' of the specie '{}' is {} bp.".format(num, specie.replace("_", " "), str(length))
                        photo = "https://i.imgur.com/RuuZ4VG.jpg"

                        NUM = num
                        LENGTH = length

                elif num.isdigit():
                    json_karyo_digit = list()

                    for e in json_karyo:
                        if e.isdigit():
                            json_karyo_digit.append(e)

                    print(len(json_karyo_digit), int(num))

                    if len(json_karyo_digit) >= int(num):
                        for e in karyotype:
                            if num == e['name']:
                                length = e['length']
                                break

                        data = "Length of chromosome '{}' of the specie '{}' is {} bp.".format(num, specie.replace("_", " "), str(length))
                        photo = "https://i.imgur.com/RuuZ4VG.jpg"

                        NUM = num
                        LENGTH = length

                    else:
                        data = "Error: chromosome not found. Check the 'Karyotype' page to know them".format(str(len(json_karyo)))
                        photo = "https://i.imgur.com/poj7xfa.jpg"

                        NUM = "key"
                        LENGTH = None

                else:
                    for e in num:
                        if e.isalpha():
                            num = num.replace(e, e.upper())

                    for i in karyotype:
                        if num == i["name"]:
                            length = i["length"]
                            break

                        else:
                            length = 'error'

                    if length == "error":
                        data = "Error: chromosome not found. There are {} chromosomes available. Check the 'Karyotype' page to know them".format(str(len(json_karyo)))
                        photo = "https://i.imgur.com/aKaXdU6.jpg"

                        NUM = "key"
                        LENGTH = None

                    else:
                        data = "Length of chromosome '{}' of the specie '{}' is {} bp.".format(num, specie.replace("_", " "), str(length))
                        photo = "https://i.imgur.com/RuuZ4VG.jpg"

                        NUM = num
                        LENGTH = length

            except KeyError:
                data = "Error: karyotype for '{}' is not available.".format(specie.replace("_", " "))
                photo = "https://i.imgur.com/poj7xfa.jpg"

                NUM = "specie"
                LENGTH = None

            json_data = dict_length(NUM, specie, LENGTH)

            with open("results.html", "r") as file:
                content = file.read().replace("OPERATION", "CHROMOSOME LENGHT").replace("IMAGE", photo).replace("HEADER", str(data)).replace("DATA", "").replace("COLOURCARD", "#ECE577")
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
                header = "Error: '{}' is not a valid gene for Homo Sapiens specie.".format(gene_input)
                data = ""
                photo = "https://i.imgur.com/aKaXdU6.jpg"

            with open("results.html", "r") as file:
                content = file.read().replace("OPERATION", "GENE SEQUENCE").replace("IMAGE", photo).replace("HEADER", header).replace("DATA", data).replace("COLOURCARD", "#EC7789")
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
                photo = "https://i.imgur.com/IITsk3C.jpg"

            except KeyError:
                header = "Error: '{}' is not a valid gene for Homo Sapiens specie.".format(gene_input)
                data = ""
                photo = "https://i.imgur.com/poj7xfa.jpg"

            with open("results.html", "r") as file:
                content = file.read().replace("OPERATION", "GENE INFORMATION").replace("IMAGE", photo).replace("HEADER", header).replace("DATA", data).replace("COLOURCARD", "#EC7789")
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

                header = "Calculations for gene '{}' is: ".format(gene_input)
                data = "<br>Lenght: {}</br><br>Percentage of Adenine: {}</br><br>Percentage of Thymine: {}</br><br>Percentage of Cytosine: {}</br><br>Percentage of Guanine: {}</br>".format(lenght, percA, percT, percC, percG)
                photo = "https://i.imgur.com/Fhayqk0.jpg"

            except KeyError:
                header = "Error: '{}' is not a valid gene for Homo Sapiens specie.".format(gene_input)
                data = ""
                photo = "https://i.imgur.com/aKaXdU6.jpg"

            with open("results.html", "r") as file:
                content = file.read().replace("OPERATION", "GENE OPERATIONS").replace("IMAGE", photo).replace("HEADER", header).replace("DATA", data).replace("COLOURCARD", "#EC7789")
                file.close()

        elif "geneList" in path:
            chromo_input = path[path.find("chromo=") + 7:path.find("&")]
            start = path[path.find("start=") + 6:path.find("&end")]
            end = path[path.find("end=") + 4:]

            try:
                chromo_data = get_json("/overlap/region/human/{}:{}-{}?content-type=application/json;feature=gene".format(chromo_input, start, end))

                try:
                    if int(start) >= int(end):
                        header = "Error: the starting point '{}' can not be bigger than the ending point '{}'.".format(start, end)
                        data = ""
                        photo = "https://i.imgur.com/poj7xfa.jpg"

                    else:
                        genes_list = list()

                        for i in range(len(chromo_data)):
                            genes_list.append("<li style=\"font-family:helvetica;font-size:90%;word-break:break-all\"><p style=\"font-weight:bold\">{}</p> ID: {}</li>".format(chromo_data[i]['external_name'], chromo_data[i]['gene_id']))

                        genes_str = "<ol>{}</ol>".format(str(genes_list).strip("[]").replace("'", "").replace(",", ""))

                        if len(genes_list) == 0:
                            header = "No genes were found for '{}-{}' interval.".format(start, end)
                            data = ""
                            photo = "https://i.imgur.com/IITsk3C.jpg"

                        else:
                            header = "{} gene(s) were found in chromosome '{}' from {} to {} position:".format(len(genes_list), chromo_input.upper(), start, end)
                            data = "{}".format(genes_str)
                            photo = "https://i.imgur.com/IITsk3C.jpg"

                except ValueError:
                    header = "Error: Invalid start or end parameter."
                    data = ""
                    photo = "https://i.imgur.com/aKaXdU6.jpg"

            except KeyError:
                if "5000000" in chromo_data["error"]:
                    header = "Error: {} is greater than the maximum allowed length interval of 5000000. Please, request smaller regions of sequence.".format(int(end)-int(start))
                    data = ""
                    photo = "https://i.imgur.com/poj7xfa.jpg"

                else:
                    header = "Error: '{}' is not a valid chromosome for Homo Sapiens specie.".format(chromo_input)
                    data = ""
                    photo = "https://i.imgur.com/aKaXdU6.jpg"

            with open("results.html", "r") as file:
                content = file.read().replace("OPERATION", "GENE LIST").replace("IMAGE", photo).replace("HEADER", header).replace("DATA", data).replace("COLOURCARD", "#EC7789")
                file.close()

        else:
            with open("error.html", "r") as file:
                content = file.read()
                file.close()

        if "json=1" in path:
            content = json.dumps(json_data)

            self.send_response(200)

            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(str.encode(content)))
            self.end_headers()

            self.wfile.write(str.encode(content))

        else:
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
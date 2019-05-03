import http.client
import json

HOST = "localhost"
PORT = 8000

# The following list contains the same endpoints where verything works fine (no imput errors) as the ones on the reports, just to check/see that these endpoints do work.

endpoints = ["listSpecies&json=1", "listSpecies?limit=10&json=1", "listSpecies?limit=1345&json=1", "listSpecies?limit=a&json=1",
             "karyotype?specie=mouse&json=1", "karyotype?specie=tiger&json=1", "karyotype?specie=fish&json=1", "karyotype?specie=2&json=1",
             "chromosomeLength?specie=mouse&chromo=18&json=1", "chromosomeLength?specie=fish&chromo=1&json=1", "chromosomeLength?specie=hello&chromo=1&json=1",
             "chromosomeLength?specie=human&chromo=30&json=1", "chromosomeLength?specie=human&chromo=asdf&json=1", "geneSeq?gene=frat1&json=1",
             "geneSeq?gene=frat24&json=1", "geneInfo?gene=fat1&json=1", "geneInfo?gene=frat3&json=1"]

for e in endpoints:
    conn = http.client.HTTPConnection(HOST, PORT)
    conn.request("GET", e)

    r1 = conn.getresponse()

    print("Response received: {}\n".format(r1.status, r1.reason))

    json_data = r1.read().decode('utf-8')

    conn.close()

    msg = json.loads(json_data)

    print("Json retrieved from {}:".format(e), msg)

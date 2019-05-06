import http.client
import json

HOST = "localhost"
PORT = 8000

# The following list contains the same endpoints as the ones on the reports,
# just to check/see that these endpoints do work.

endpoints = ["listSpecies?json=1", "/listSpecies?limit=10&json=1", "listSpecies?limit=a&json=1", "listSpecies?limit=1234&json=1",
             "karyotype?specie=mouse&json=1", "karyotype?specie=guinea+pig&json=1", "karyotype?specie=fish&json=1", "karyotype?specie=1%2B2&json=1",
             "chromosomeLength?specie=mouse&chromo=18&json=1", "chromosomeLength?specie=human&chromo=33&json=1", "/chromosomeLength?specie=fish&chromo=33&json=1", "chromosomeLength?specie=guinea+pig&chromo=33&json=1",
             "geneSeq?gene=frat1&json=1", "geneSeq?gene=fat5&json=1",
             "geneInfo?gene=frat1&json=1", "geneInfo?gene=frat3&json=1",
             "geneCalc?gene=frat1&json=1", "geneCalc?gene=frat3&json=1",
             "geneList?chromo=1&start=0&end=30000&json=1", "geneList?chromo=abcd&start=12000&end=130000&json=1", "geneList?chromo=1&start=20&end=15&json=1", "geneList?chromo=1&start=1234&end=7654321&json=1", "geneList?chromo=y&start=1&end=a&json=1",
             "geneBases&json=1"]

for e in endpoints:
    conn = http.client.HTTPConnection(HOST, PORT)
    conn.request("GET", e)

    r1 = conn.getresponse()

    print("Response received: {}".format(r1.status, r1.reason))

    json_data = r1.read().decode('utf-8')

    conn.close()

    msg = json.loads(json_data)

    print("Json retrieved from {}:".format(e), msg, "\n")

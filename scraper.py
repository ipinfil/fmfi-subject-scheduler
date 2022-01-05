"""
VAROVANIE! Odporny kod, scraper pouzivany iba na tvorbu faktov v knowledge base. Prosim necitat!
Resp. iba na vlastne nebezpecenstvo. :)
"""
import unicodedata
from typing import final
from bs4 import BeautifulSoup


def repair(s: str):
    return s.lower().replace("-", "_").replace("/", "_")


def predmety():
    global final_rows
    for row in final_rows:
        tds = list(row.children)
        name = list(tds[3].children)[0].contents[0]
        try:
            year = tds[5].contents[0][0].replace("/", "0")
        except:
            year = "0"

        try:
            sem = tds[5].contents[0][-1].replace("/", "n").lower()
        except:
            sem = "n"

        try:
            cr = tds[7].contents[0].replace("kr", "")
        except:
            cr = "_"

        line = (
            f'predmet({repair(tds[0].contents[0][2:])}, "{name}", {year}, {sem}, {cr}).'
        )
        print(line)


def predmety_ucitelia():
    global final_rows
    ucitelia_map = {}
    for row in final_rows:
        tds = list(row.children)
        try:
            names = list(tds[3].children)[1][2:].strip().split(", ")
        except:
            continue

        for n in names:
            p = False
            if not ucitelia_map.get(
                ucitel_id(n) + repair(tds[0].contents[0][2:]), False
            ):
                p = True

            ucitelia_map[ucitel_id(n) + repair(tds[0].contents[0][2:])] = True

            if p:
                print(
                    f"predmet_ucitel({repair(tds[0].contents[0][2:])}, {ucitel_id(n)})."
                )


def ucitel_id(ucitel):
    return (
        unicodedata.normalize("NFKD", ucitel.lower().replace(". ", ""))
        .encode("ASCII", "ignore")
        .decode()
        .replace(" ", "")
    )


def ucitelia():
    global final_rows
    ucitelia_map = {}

    for row in final_rows:
        tds = list(row.children)
        try:
            name = list(tds[3].children)[1][2:].strip().split(", ")
        except:
            continue

        for n in name:
            p = False
            if not ucitelia_map.get(ucitel_id(n), False):
                p = True

            ucitelia_map[ucitel_id(n)] = f'ucitel({ucitel_id(n)}, "{n}").'

            if p:
                print(ucitelia_map[ucitel_id(n)])


final_rows = []
with open("ain.html") as f:
    html = BeautifulSoup(f, "lxml")
    rows = html.find_all("tr")
    for row in rows:
        children = [td for td in list(row.children) if td != "\n"]

        if len(children) == 6:
            final_rows.append(row)

# predmety()
# ucitelia()
predmety_ucitelia()

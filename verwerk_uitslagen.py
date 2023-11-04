# Geschreven door Marleen  Juli 2023
def score(lijn: str) -> tuple:  # wie, punten, dames
    # haal de informatie uit 1 lijn van het .csv bestand
    # wie, punten, dames :  naam, lijst met punten vb [3,6,1,10] , aantal dames deze maane
    # indien lijn niet zinvol: "geen lid"
    if ";" in lijn:
        kolommen = lijn.split(";")
    else:
        kolommen = lijn.split(",")
    if len(kolommen) < 20:
        return "geen lid"
    wie = kolommen[0]
    punten_str = kolommen[2:6]
    punten = []
    for p in punten_str:
        try:
            if len(p) and p.isdigit() > 0:
                punten.append(int(p))

            else:
                punten.append(0)
        except Exception:
            print(wie, punten_str)
            print("fout:", lijn)
            k = input("stop")
    # uitgeloot en laatste wedstrijd gespeeld
    if punten[3] != 0 and 0 in punten[0:3]:
        p = punten.index(0)
        punten[p] = punten[3]
        punten[3] = 0

    # dames in kolom 16,17,18,19
    try:
        dames = sum([int(p.strip()) for p in kolommen[16:20] if len(p.strip()) > 0])

        if len(wie) > 0 and wie[0].upper() != "Z":  # echt lid
            return wie, punten, dames
        else:
            return "geen lid"
    except Exception as e:
        print(lijn)


def verwerk(bn: str) -> tuple:  # (scores_maand, dames_maand)
    # leest het bestand in en bepaalt de scores, en de dames voor die maand
    # scores_maand mapt de naam op de score van één maand vb [1,3,0,10] of [0,0,0,0]
    # dames_maand mapt de naam op het totaal aantal dames voor die maand
    scores_maand = {}  # dictionary voor de scores
    dames_maand = {}  # dictionary voor totaal aantal dames deze maand

    with open(bn) as invoer:
        eerstelijn = invoer.readline()  # twee lijnen zonder informatie
        tweedelijn = invoer.readline()
        for lijn in invoer:
            tup = score(lijn)
            if len(tup) == 3:  # bevat informatie van een lid
                wie, punten, dames = tup
                if len(wie) > 2:
                    scores_maand[wie] = punten
                    dames_maand[wie] = dames
        return scores_maand, dames_maand


# opsomming van de bestandsnamen
maanden = [
    "September",
    "Oktober",
    "November",
    "December",
    "Januari",
    "Februari",
    "Maart",
    "April",
    "Mei",
    "Juni",
]
# korte naam voor in het html-bestand
maanden_kort = [m[0:3] for m in maanden]

# telt het aantal positieve punten in de uitslagen
# uitslagen=[[1,3,0,10],...] lijst van lijst met gehele getallen (aantal getallen maakt niet uit)
def tel_punten(uitslagen: list) -> int:
    tel = 0
    for punten in uitslagen:
        for p in punten:
            if p > 0:
                tel += 1
    return tel


def verwerk_klassement(jaar: str, laatste_maand: int) -> tuple:  # maandelijks, dames
    # leest de maandelijkse uitslagen (tot en met laatste_maand)
    # maandelijks: mapt de naam op de lijst met lijst van maximum 4 scores voor elke maand
    # maximaal 30 scores worden onthouden in de lijst!
    # dames: mapt de naam op een lijst met het aantal dames per maand
    maandelijks = {}
    dames = {}
    for i in range(laatste_maand):
        maand = maanden[i]
        scores_maand, dames_maand = verwerk(f"{jaar}\{maand}.csv")
        for wie, punten in scores_maand.items():
            if not wie in maandelijks:  # voeg eerste maanden toe
                maandelijks[wie] = []
                dames[wie] = []
                for k in range(i):
                    maandelijks[wie].append([0, 0, 0, 0])
                    dames[wie].append(0)
            gespeeld = tel_punten(maandelijks[wie])
            # nooit meer dan 30 scores overnemen
            if gespeeld < 30:
                aantal = min(4, 30 - gespeeld)
                maandelijks[wie].append(punten[0:aantal])
            dames[wie].append(dames_maand[wie])
    return maandelijks, dames


def maak_punten(uitslagen: list, laatste_maand: int) -> list:
    # uitslagen bevat de maandelijkse score van 1 lid, vb [[1,3,0,10],...]
    # uitslagen bevat maximaal 30 scores (>0)
    # enkel de punten tot en met laatste_maand worden verwerkt
    # punten_per_maand is een lijst met voor elke maand een lijst met exact 3 punten
    # achteraan staat een lijst met de resterende reservepunten
    # vb. punten_per_maand = [[1,3,10],[6,3,1],[1,1,1],[1,3]] #3 maanden + 2 reservepunten
    punten_per_maand = []
    for punten in uitslagen:
        score = punten[:3]  # maximum drie eerste punten
        while len(score) < 3:  # vul aan tot 3 punten met nullen
            score.append(0)
        punten_per_maand.append(score)
    # voeg drie nullen toe voor ontbrekende maanden
    while len(punten_per_maand) != laatste_maand:
        punten_per_maand.append([0, 0, 0])
    # verzamel de reservepunten uit de uitslagen
    reserve = []
    for punten in uitslagen:
        if len(punten) == 4 and punten[3] > 0:
            reserve.append(punten[3])  # vierde punt
    # reserve-spellen inzetten waar nu een 0 staat
    tel = 0
    for i in range(len(punten_per_maand)):
        for j in range(3):  # kijk of een 0 staat in de drie scores
            if punten_per_maand[i][j] == 0:
                if tel < len(reserve):  # is er nog reserve?
                    punten_per_maand[i][j] = reserve[tel]
                    tel += 1
    niet_ingezet = reserve[tel:]  # kan leeg zijn
    punten_per_maand.append(niet_ingezet)  # voeg de reserve_punten achteraan toe
    # print(punten_per_maand, "\n")
    return punten_per_maand


def html_string(l: list, sep: str) -> str:
    # zet sep tussen de items in de lijst l - l kan getallen bevatten
    if len(l) == 0:
        return ""
    res = ""
    for v in l:
        res += str(v) + sep
    return res[: -len(sep)]


def add_hoofding(bestand, maand: str, jaar: str):
    # voegt de eerste lijnen voor html-code toe in het bestand
    with open("hulp\\hoofding.html") as hoofding:
        for lijn in hoofding.readlines():
            if "maand" in lijn:
                lijn = lijn.replace("maand", maand)  # juiste maand in de titel

            if "jaar" in lijn:
                lijn = lijn.replace("jaar", jaar)  # juist jaar in de titel
            print(lijn.strip(), file=bestand)


def maak_html_lijnen(
    maandelijks: dict, punten_per_maand: dict, laatste_maand: int
) -> dict:  # html_lijnen
    # informatie die voor elk lid in de html-file moet (niet geordend)
    # maandelijks mapt de naam op alle scores behaald in elke maand
    # punten_per_maand mapt de naam op de drie punten die tellen voor elke maand + reservepunten
    # punten_per_maand[wie] = [[1,3,10],...,[10,6,3], [6,3]]
    # html_lijnen mapt de naam op de html-string die in de tabel moet toegevoegd worden
    html_lijnen = {}
    rijhoogte_stijl = 'style="height: 10px;"'
    for wie in punten_per_maand:
        # print(f"{wie}: {tel_punten(punten_per_maand[wie])} : {maandelijks[wie]}")
        # lijst met de scores behaald in elke maand die verwerkt moet worden
        uitslagen = punten_per_maand[wie]  # drie punten per maand+reservepunten
        scores = [sum(s) for s in uitslagen[0:laatste_maand]]
        # zijn er reservepunten?
        if len(uitslagen) > laatste_maand:  # er zijn reserve-punten_per_maand
            reserve = uitslagen[laatste_maand]
        else:
            reserve = []
        details = []  # wat is deze maand gespeeld - maandelijks is per maand
        # enkel scores die meetellen en die positief zijn
        if len(maandelijks[wie]) >= laatste_maand:
            details = [p for p in maandelijks[wie][laatste_maand - 1] if p > 0]
        # aantal boompjes in het klassement
        aantal_boompjes = tel_punten(uitslagen[0:laatste_maand])
        # maak nu de html-code voor deze persoon:

        lijn_html = f"{wie.replace('é','&eacute;')}<th>{aantal_boompjes}\n"
        lijn_html += f'<td style="text-align: center;font-style: italic;"><nobr>{html_string(details,"/")}</nobr>\n'
        lijn_html += f'<td style="text-align: center;font-style: italic;">{html_string(reserve,"/")}\n'

        scores_html = "<td>" + html_string(scores, "<td>")
        p = scores_html.rfind("<td>")  # opmaak bij laatste score toevoegen
        scores_html = (
            scores_html[0:p]
            + '<td style="background-color: orange">'
            + scores_html[p + 4 :]
        )
        lijn_html += f"{scores_html}\n"

        lijn_html += f"<th>{sum(scores)}\n"
        if len(wie) > 2:
            html_lijnen[wie] = lijn_html  # onthoud in dictionary
    return html_lijnen


def maak_klassement_bestand(html_lijnen: dict, jaar: str, laatste_maand: int):
    # maakt het klassement voor de gevraagd maand, en het opgegeven jaar
    # html_lijnen bevat voor elk lid de html-string die in de tabel moet
    maand = maanden[laatste_maand - 1]
    with open(f"{jaar}_Website\{maand}.html", "w") as html:
        # add_hoofding(html, maand, jaar)
        print(f"<h1>{maand} {jaar}</h1>", file=html)
        print("<table border=1>", file=html)
        # voeg de titels van de tabel toe
        print("<tr><th>naam<th>GS<th>detail<th>extra", file=html)
        print(f'<td>{html_string(maanden_kort[:laatste_maand], "<td>")}', file=html)
        print("<th>TOT", file=html)
        # voeg de lijnen toe
        nr = 1
        for wie in html_lijnen:
            print(f"<tr><td>{nr}) {html_lijnen[wie]}", file=html)
            nr += 1
        print("</table>", file=html)
        # print("</body>", file=html)
        # print("</html>", file=html)
        # melding waar het bestand staat
        print(f"{jaar}_Website\{maand}.html gewijzigd")


def maak_pdf(bestandsnaam: str) -> None:
    # Your existing functions and code...
    import pdfkit

    # bestandsnaam is pad, bvb f"{jaar}_Website\\{naam}.html"
    # maakt  f"{jaar}_pdf\\{naam}.pdf
    # Generate PDF from the HTML file
    html_file = bestandsnaam  # f"{jaar}_Website\\{maand}.html"
    pdf_file = html_file.replace("Website", "pdf").replace(
        ".html", ".pdf"
    )  # f"{jaar}_pdf\\{maand}.pdf"

    try:
        print(f"{html_file} -> {pdf_file}")
        pdfkit.from_file(html_file, pdf_file, options={"enable-local-file-access": ""})
        print(f"{pdf_file} generated.")
    except Exception as e:
        print(e)


def maak_html(jaar: str, laatste_maand: int):
    try:
        maandelijks, dames = verwerk_klassement(jaar, laatste_maand)
        # punten_per_maand per lid -> lijst met 3 scores die meetellen voor die maand - reserve staat achteraan
        punten_per_maand = {}
        for wie in maandelijks:
            punten_per_maand[wie] = maak_punten(maandelijks[wie], laatste_maand)
        # punten_per_maand[wie] = [[1,3,10],...,[10,6,3], [6,3]]
        # informatie die voor elk lid in de html-file moet (niet geordend)
        # beperk tot de laatste_maand
        html_lijnen = maak_html_lijnen(maandelijks, punten_per_maand, laatste_maand)
        # de score voor elk lid
        score = {}
        for wie in punten_per_maand:
            score[wie] = sum([sum(s) for s in punten_per_maand[wie][0:laatste_maand]])
        # Sort the dictionary by values in ascending order
        scores_gesorteerd = dict(
            sorted(score.items(), key=lambda x: x[1], reverse=True)
        )
        for wie in scores_gesorteerd:
            scores_gesorteerd[wie] = html_lijnen[wie]
        maak_klassement_bestand(scores_gesorteerd, jaar, laatste_maand)
    except FileNotFoundError:
        print(f"Er ontbreken maanden")


def maak_overzicht_dames(jaar: int, maand: str, dames: dict):
    with open(f"{jaar}_Website\Dames.html", "w") as html:
        print(f"<html>\n<body>", file=html)
        print(f"<h1>Dames totaal</h1>", file=html)
        print(f"<ol>", file=html)
        dames_gesorteerd = dict(
            sorted(dames.items(), key=lambda x: sum(x[1]), reverse=True)
        )
        for wie, aantal in dames_gesorteerd.items():

            print(
                f"<li>{wie}: {sum(aantal)} </li>",
                file=html,
            )
            # print(f"<li>{wie}:{sum(aantal)} </li>", file=html)
        print("</ol></body></html>", file=html)
        print(f"{jaar}_Website\Dames.html gemaakt")


# controle_bestand_laatste maand maken
# maakt ook rangschikking dames tot die maand
def maak_controle_bestand(jaar: str, laatste_maand: int):
    maandelijks, dames = verwerk_klassement(jaar, laatste_maand)
    maak_overzicht_dames(jaar, maanden[laatste_maand - 1], dames)
    if laatste_maand == 1:
        print("Geen controlebestand gemaakt")
        return ""
    # punten_per_maand per lid -> lijst met 3 scores die meetellen voor die maand - reserve staat achteraan
    punten_per_maand = {}

    for wie in maandelijks:
        punten_per_maand[wie] = maak_punten(maandelijks[wie], laatste_maand)
    html_lijnen = maak_html_lijnen(maandelijks, punten_per_maand, laatste_maand)

    # vorige stand
    maandelijks, _ = verwerk_klassement(jaar, laatste_maand - 1)
    punten_per_maand = {}
    for wie in maandelijks:
        punten_per_maand[wie] = maak_punten(maandelijks[wie], laatste_maand - 1)

    html_lijnen_vorig = maak_html_lijnen(
        maandelijks, punten_per_maand, laatste_maand - 1
    )
    maand = maanden[laatste_maand - 1]
    vorige_maand = maanden[laatste_maand - 2]
    with open(f"Controle.html", "w") as html:
        print(
            '<head>\n<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />',
            file=html,
        )
        print('<link rel="stylesheet" type="text/css" href="extra.css" />', file=html)
        print(f"<title>Controle voor {maand}</title>", file=html)
        print("</head>\n<body>", file=html)
        print("<table border=1>", file=html)
        print(f"<tr><td>{vorige_maand} {jaar} <td>{maand} {jaar}", file=html)

        print("<tr><td><table border=1>", file=html)
        print("<tr><th>naam<th>GS<th>detail<th>extra", file=html)
        print(f'<td>{html_string(maanden_kort[:laatste_maand-1], "<td>")}', file=html)
        print("<th>TOT", file=html)
        for wie in html_lijnen_vorig:
            print(f"<tr><td>{html_lijnen_vorig[wie]}", file=html)
        print("</table>", file=html)

        print("<td><table border=1>", file=html)
        print("<tr><th>naam<th>GS<th>detail<th>extra", file=html)
        print(f'<td>{html_string(maanden_kort[:laatste_maand], "<td>")}', file=html)
        print("<th>TOT", file=html)
        for wie in html_lijnen:
            print(f"<tr><td>{html_lijnen[wie]}", file=html)
        print("</table></html>", file=html)

        print("</body>", file=html)
        print("</html>", file=html)
        # enkel tot laatste_maand
        print(f"Controle.html gewijzigd voor {maanden[laatste_maand-1]}")


import os


def main():
    jaar = input("Welk jaar ?")
    pdf = input("Met pdf (Ja/Nee)? ").lower() != "nee"
    if os.path.exists(jaar):
        if not os.path.exists(f"{jaar}_Website"):
            os.makedirs(f"{jaar}_Website")
            os.makedirs(f"{jaar}_pdf")
            # print(f"copy 2022_Website\\extra.css {jaar}_Website\\")
            os.popen(f"copy hulp\\extra.css {jaar}_Website\\")
        aantal = int(input("Hoeveel maanden?"))
        for i in range(aantal):
            maak_html(jaar, i + 1)
            if pdf:  # Generate PDF from the HTML file
                maand = maanden[i]
                html_file = f"{jaar}_Website\\{maand}.html"
                maak_pdf(html_file)
        maak_controle_bestand(jaar, aantal)
        if pdf:
            maak_pdf(f"{jaar}_Website\Dames.html")
    else:
        print(f"de folder {jaar} bestaat niet")


main()

import csv
import os.path
import re

from bs4 import BeautifulSoup

DIR = "strony"

csv_obwody     = open('pkw-obwody.csv',     'w', encoding="UTF-8", newline='')
csv_prezydenci = open('pkw-prezydenci.csv', 'w', encoding="UTF-8", newline='')
csv_radni      = open('pkw-radni.csv',      'w', encoding="UTF-8", newline='')

csv_obwody_writer     = csv.writer(csv_obwody,     delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
csv_prezydenci_writer = csv.writer(csv_prezydenci, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
csv_radni_writer      = csv.writer(csv_radni,      delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

csv_obwody_writer.writerow(['Nr obwodu', 'Nazwa', 'Siedziba', 'Typ', 'Granice', 'Liczba mieszkańców', 'Liczba wyborców',
                            'PR - liczba wyborców', 'PR - liczba kart w urnie', 'RM - liczba wyborców',
                            'RM - liczba kart w urnie'])
csv_prezydenci_writer.writerow(['Nr obwodu', 'Kandydat', 'Liczba głosów'])
csv_radni_writer.writerow(['Nr obwodu', 'Komitet wyborczy', 'Kandydat', 'Liczba głosów'])

files = [f for f in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, f))]
files.sort(key=int)

for file_name in files:

    print("File: {0}".format(file_name))
    s = BeautifulSoup(open(os.path.join(DIR, file_name), encoding="UTF-8"), "html.parser")

    # Informacje o obwodowej komisji wyborczej

    okw_t = s.find('table', class_='stat_table')
    okw_t_tds = okw_t.find_all('td')

    okw_numer               = int(file_name)
    okw_nazwa, okw_siedziba = okw_t_tds[1].text.split(', ')
    okw_typ                 = okw_t_tds[3].text
    okw_granice             = okw_t_tds[7].text
    okw_liczba_mieszkancow  = int(okw_t_tds[9].text)
    okw_liczba_wyborcow     = int(okw_t_tds[11].text)

    # Protokoly

    protokol_pr_id = re.compile('\d+').search(s.find('li', class_=re.compile('tab_button_protocol_'),
                                                     text=re.compile('Wybory Prezydenta Miasta'))['class'][0]
                                             ).group()
    protokol_rm_id = re.compile('\d+').search(s.find('li', class_=re.compile('tab_button_protocol_'),
                                                     text=re.compile('Wybory Rady Miasta'))['class'][0]
                                              ).group()

    # Prezydent

    p_pr = s.find('div', class_='tab_box_protocol_' + protokol_pr_id)

    tmp = p_pr.find_all('td', limit = 51)

    pr_liczba_wyborcow     = int(tmp[2].text)
    pr_liczba_kart_w_urnie = int(tmp[50].text)

    for row in p_pr.find('table', class_='stat_table_dt').find('tbody').find_all('tr'):
        row_tds = row.find_all('td')
        pr_kandydat_nazwisko = str(row_tds[1].contents[0].contents[1])
        pr_kandydat_wynik    = int(str(row_tds[5].contents[1]).replace(' ', ''))

        csv_prezydenci_writer.writerow([okw_numer, pr_kandydat_nazwisko, pr_kandydat_wynik])

    # Rada Miasta

    p_rm = s.find('div', class_='tab_box_protocol_' + protokol_rm_id)

    tmp = p_rm.find_all('td', limit=51)

    rm_liczba_wyborcow     = int(tmp[2].text)
    rm_liczba_kart_w_urnie = int(tmp[50].text)

    csv_obwody_writer.writerow(
        [okw_numer, okw_nazwa, okw_siedziba, okw_typ, okw_granice, okw_liczba_mieszkancow, okw_liczba_wyborcow,
         pr_liczba_wyborcow, pr_liczba_kart_w_urnie, rm_liczba_wyborcow, rm_liczba_kart_w_urnie])

    rm_komitety_nazwy = [kom.text.strip().split(' - ')[1] for kom in p_rm.find_all('header', class_='stat_header')]
    rm_komitety_kandydaci = p_rm.find_all('table', class_='stat_table_dt')

    for i, kom in enumerate(rm_komitety_kandydaci):
        rm_kandydat_komitet = rm_komitety_nazwy[i]
        for kan in kom.find('tbody').find_all('tr'):
            row_tds = kan.find_all('td')
            rm_kandydat_nazwisko = str(row_tds[1].contents[0].contents[1])
            rm_kandydat_wynik    = int(str(row_tds[5].contents[1]).replace(' ', ''))

            csv_radni_writer.writerow([okw_numer, rm_kandydat_komitet, rm_kandydat_nazwisko, rm_kandydat_wynik])

csv_obwody.close()
csv_prezydenci.close()
csv_radni.close()

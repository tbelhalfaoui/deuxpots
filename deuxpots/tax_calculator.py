from dataclasses import dataclass

from bs4 import BeautifulSoup
import requests as rq

SIMULATOR_URL = 'https://simulateur-ir-ifi.impots.gouv.fr/cgi-bin/calc-2023.cgi'


@dataclass
class SimulatorResult:
    rate: float             # Taux du prélèvement à la source (foyer)
    total_tax: float        # Impôt total (net)
    already_paid: float    # Montant déjà payé
    remains_to_pay: float   # Reste à payer


def _simulator_api(box_data):
    resp = rq.post(SIMULATOR_URL, data=box_data)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text)
    return {input['name']: input['value']
            for input in soup.select('input[type=hidden]')}


def _format_simulator_results(results):
    RASTXFOYER = float(results["RASTXFOYER"])/100
    INETIR = int(results.get("IINETIR", 0))
    IINET = int(results['IINET'])
    IREST = int(results['IREST'])
    remains_to_pay = IINET - IREST
    return SimulatorResult(
        rate=RASTXFOYER,
        total_tax=INETIR,
        already_paid=INETIR - remains_to_pay,
        remains_to_pay=remains_to_pay,
    )

def compute_tax(box_data):
    results = _simulator_api(box_data)
    return _format_simulator_results(results)
    
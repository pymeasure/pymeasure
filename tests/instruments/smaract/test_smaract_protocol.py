import pytest
from pymeasure.test import expected_protocol
from pymeasure.units import ureg
from pymeasure.instruments.smaract.scu_ascii import SmarActSCU_USB
def test_init():
    """Vérifie que l'initialisation ne plante pas."""
    with expected_protocol(
        SmarActSCU_USB,
        [] # Aucune commande n'est envoyée au __init__ dans notre driver
    ) as inst:
        pass

def test_id():
    """Vérifie la commande GID."""
    with expected_protocol(
        SmarActSCU_USB,
        [(":GID", ":ID123456")] # Commande envoyée, Réponse simulée
    ) as inst:
        assert inst.id == "123456"

def test_position_getter():
    """Vérifie la lecture de la position (Parsing)."""
    with expected_protocol(
        SmarActSCU_USB,
        [(":GP0", ":P0P-500.5")] # On simule une réponse négative
    ) as inst:
        assert inst.position == -500.5

def test_position_setter():
    """Vérifie l'écriture de la position (Commande MPA)."""
    with expected_protocol(
        SmarActSCU_USB,
        [(":MPA0P1000H0", None)] # None car pas de réponse attendue pour un Setter
    ) as inst:
        inst.position = 1000

def test_move_relative_with_units():
    """Vérifie que les unités (mm) sont bien converties en microns."""
    with expected_protocol(
        SmarActSCU_USB,
        [(":MPR0P2000.0H0", None)] # 2 mm = 2000 microns
    ) as inst:
        inst.move_relative(2 * ureg.mm)

def test_frequency_max():
    """Vérifie la propriété frequency_max."""
    with expected_protocol(
        SmarActSCU_USB,
        [(":GCLF0", ":CLF0F5000")] # Réponse typique du manuel
    ) as inst:
        assert inst.frequency_max == 5000
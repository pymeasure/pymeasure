import time
import pytest
from pymeasure.generator import Generator
from pymeasure.instruments.smaract.scu_ascii import SmarActSCU_ASCII
generator = Generator()
inst = generator.instantiate(TC038, adapter, 'hcp', adapter_kwargs={'baud_rate': 9600})

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here





# Cette fixture est MAGIQUE : elle permet de sauter ces tests
# si aucune adresse n'est donnée en ligne de commande.
@pytest.fixture(scope="module")
def smaract('ASRL3::INSTR'):
    instr = SmarActSCU_ASCII('ASRL3::INSTR')
    return instr


def test_connection(smaract):
    """Vérifie simplement qu'on peut lire l'ID."""
    print(f"ID détecté : {smaract.id}")
    assert smaract.id != ""


def test_status_initial(smaract):
    """Vérifie le statut (S=Stopped, normalement)."""
    status = smaract.get_status()
    assert status in ['S', 'M', 'H', 'T']


def test_small_move(smaract):
    """
    Test un vrai mouvement physique.
    ATTENTION : Assurez-vous que la platine peut bouger sans danger !
    """
    initial_pos = smaract.position

    # On bouge de 10 microns
    smaract.move_relative(10)

    # On attend un peu que ça bouge
    time.sleep(0.5)

    # On vérifie que la position a changé
    new_pos = smaract.position
    assert abs(new_pos - initial_pos) > 0.1  # Tolérance

if __name__ == '__main__':
    unittest.main()

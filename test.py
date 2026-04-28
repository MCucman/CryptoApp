import unittest
from backend import filter_by_change 


class TestCryptoLogic(unittest.TestCase):
    def setUp(self):
        # Priprema filtera od 5% za USD
        self.filter = filter_by_change(5.0, "usd")

    def test_filter_pass(self):
        """Testira valutu koja ima veliku promjenu (treba proći)."""
        podatak = {"usd_24h_change": 10.2}
        self.assertTrue(self.filter(podatak))

    def test_filter_fail(self):
        """Testira valutu koja ima malu promjenu (ne smije proći)."""
        podatak = {"usd_24h_change": 1.5}
        self.assertFalse(self.filter(podatak))

    def test_filter_negative_change(self):
        """Testira radi li abs() (pad od 7% je isto značajan)."""
        podatak = {"usd_24h_change": -7.0}
        self.assertTrue(self.filter(podatak))

if __name__ == "__main__":
    unittest.main()
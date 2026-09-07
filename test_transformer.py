"""Unit tests for Bhola Updates forwarder bot message transformer."""
import unittest
from transformer import process_message

class TestTransformer(unittest.TestCase):

    def test_all_results_transformation(self):
        source = """🔠🔠🔠🔠〰️5️⃣6️⃣7️⃣
19/08/2026 (WEDNESDAY)
ALL RESULTS
👉👉DAY RESULTS
SRIDEVI 400-49-360
TIME BAZAR 149-46-556
MADHUR DAY 344-19-577
MILAN DAY 145-02-345
RAJDHANI DAY 788-36-259
SUPREME DAY 770-46-600
KALYAN 278-73-247
👉👉NIGHT RESULTS
SRIDEVI NIGHT 579-11-245
MADHUR NIGHT 359-71-227
SUPREME NIGHT 455-47-359
MILAN NIGHT 890-79-270
KALYAN NIGHT 256-34-347
RAJDHANI NIGHT 116-82-480
MAIN BAZAR 569-00-334
https://bhai567.org
https://bhai567.org"""

        expected = """🔱BHOLA UPDATES🔱
19/08/2026 (WEDNESDAY)
ALL RESULTS
🌞DAY RESULTS🌞
SRIDEVI 400-49-360
TIME BAZAR 149-46-556
MADHUR DAY 344-19-577
MILAN DAY 145-02-345
RAJDHANI DAY 788-36-259
KALYAN 278-73-247
🌕NIGHT RESULTS🌕
SRIDEVI NIGHT 579-11-245
MADHUR NIGHT 359-71-227
MILAN NIGHT 890-79-270
KALYAN NIGHT 256-34-347
RAJDHANI NIGHT 116-82-480
MAIN BAZAR 569-00-334
🔱BHOLA UPDATES🔱"""

        should_fwd, output = process_message(source)
        self.assertTrue(should_fwd)
        self.assertEqual(output.strip(), expected.strip())

    def test_single_market_fast_update(self):
        source = """🔥 TIME BAZAR 🔥
╭───── ✦ ─────╮
🎯 126 - 90 - 127 🎯
╰───── ✦ ─────╯
⚡ SUPER FAST UPDATE ⚡
🚀 सबसे पहले • सबसे तेज़ 🚀"""

        expected = """💰TIME BAZAR 💰
╭───── ✦ ─────╮
🎯 126 -- 90 -- 127 🎯
╰───── ✦ ─────╯
🔱BHOLA UPDATES🔱"""

        should_fwd, output = process_message(source)
        self.assertTrue(should_fwd)
        self.assertEqual(output.strip(), expected.strip())

    def test_good_night(self):
        source = """💤 Good Night Dosto! Aaram se soyein, kal milte hain naye result ke saath 🌙
✨ Kismat unhi ka saath deti hai jo har din try karte hain — aap mein woh hai."""

        expected = """😴 GOOD NIGHT 😴
KAL PHIR SE NAYE SHURUAAT"""

        should_fwd, output = process_message(source)
        self.assertTrue(should_fwd)
        self.assertEqual(output.strip(), expected.strip())

    def test_good_morning(self):
        source = """🌅 Good Morning Dosto! Naya din, naya result, naya luck — chaliye shuru karte hain ✨
✨ Risk lene se hi reward milta hai — aaj kuch naya try kijiye."""

        expected = """🌄 GOOD MORNING 🌄"""

        should_fwd, output = process_message(source)
        self.assertTrue(should_fwd)
        self.assertEqual(output.strip(), expected.strip())

    def test_promo_app_download(self):
        source = """🙁🙁☹️😶🙁☹️😏😣
🔠🔠🔠🔠〰️5️⃣6️⃣7️⃣
🚩🚩GUJRAT NO.1🚩🚩
➡️भरोसेमंद मटका एप्लीकेशन 👈
MINIMUM DEPOSIT 😀😀😀
MINIMUM WITHDRAWAL😏😂😂
डाउनलोड करिए BHAI 567 एप्लिकेशन
➡️ https://bhai567.org ⬅️
➡️ https://bhai567.org ⬅️
➡️ https://bhai567.org ⬅️
🔼🔼🔼🔼🔼🔼🔼
DOWNLOAD LINK UPER DI HAI
🔼🔼🔼🔼🔼🔼"""

        expected = """BHOLA JI OFFICE
CUTTING CONTACT := 7697113466 💬
*──────⊱◈◈◈⊰──────*
सबसे ज्यादा रेट के साथ ऑनलाइन खेले और दिन मै अपनी जीती हुई राशि निकले*
💵*सिंगल अंक 100रु का 1000रु*
💵*जोड़ी 100रु का 10000रु*
💵*सिंगल पाना का 100रु का 15000रु*
💵*डबल पाना का 100रु का 30000रु*
💵*ट्रिपल पाना का 100रु का 50000रु*
💵*आधा संगम का 10रु का 10000रु*
💵*पुरा संगम का 10रु का 100000रु*"""

        should_fwd, output = process_message(source)
        self.assertTrue(should_fwd)
        self.assertEqual(output.strip(), expected.strip())

    def test_unrelated_message_ignored(self):
        unrelated = [
            "Random chat message from user",
            "Hey guys check this video",
            "Vote in this poll below:",
            "Just an announcement about rules"
        ]
        for msg in unrelated:
            should_fwd, output = process_message(msg)
            self.assertFalse(should_fwd, f"Expected '{msg}' to be ignored.")

if __name__ == "__main__":
    unittest.main()

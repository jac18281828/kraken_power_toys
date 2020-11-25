from unittest import TestCase
from kraken_book import KrakenBookWss
import asyncio


EXAMPLE_SNAPSHOT = """
[
  0,
  {
    "as": [
      [
        "5541.30000",
        "2.50700000",
        "1534614248.123678"
      ],
      [
        "5541.80000",
        "0.33000000",
        "1534614098.345543"
      ],
      [
        "5542.70000",
        "0.64700000",
        "1534614244.654432"
      ]
    ],
    "bs": [
      [
        "5541.20000",
        "1.52900000",
        "1534614248.765567"
      ],
      [
        "5539.90000",
        "0.30000000",
        "1534614241.769870"
      ],
      [
        "5539.50000",
        "5.00000000",
        "1534613831.243486"
      ]
    ]
  },
  "book-100",
  "XBT/USD"
]
"""

EXAMPLE_U0 = """
[
  1234,
  {
    "a": [
      [
        "5541.30000",
        "2.50700000",
        "1534614248.456738"
      ],
      [
        "5542.50000",
        "0.40100000",
        "1534614248.456738"
      ]
    ],
    "c": "2756009329"
  },
  "book-10",
  "XBT/USD"
]
"""

EXAMPLE_U1 = """
[
  1234,
  {
    "a": [
      [
        "5541.30000",
        "2.50700000",
        "1534614248.456738"
      ],
      [
        "5542.50000",
        "0.40100000",
        "1534614248.456738"
      ]
    ]
  },
  {
    "b": [
      [
        "5541.30000",
        "0.00000000",
        "1534614335.345903"
      ]
    ],
    "c": "2756009329"
  },
  "book-10",
  "XBT/USD"
]
"""

EXAMPLE_R1 = """
[
  1234,
  {
    "a": [
      [
        "5541.30000",
        "2.50700000",
        "1534614248.456738",
        "r"
      ],
      [
        "5542.50000",
        "0.40100000",
        "1534614248.456738",
        "r"
      ]
    ],
    "c": "2756009329"
  },
  "book-25",
  "XBT/USD"
]
"""



class checksum_test(TestCase):

    def setUp(self):
        self.book_wss = KrakenBookWss()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def test_kraken_example1(self):

     self.loop.run_until_complete(self.book_wss.on_message(None, EXAMPLE_SNAPSHOT))
     
     self.loop.run_until_complete(self.book_wss.on_message(None, EXAMPLE_U0))
     book_crc32 = self.book_wss.book_checksum()
     self.assertEquals(2756009329, book_crc32)
     self.assertTrue(self.book_wss.is_running)


    def test_kraken_example2(self):

     self.loop.run_until_complete(self.book_wss.on_message(None, EXAMPLE_SNAPSHOT))
     
     self.loop.run_until_complete(self.book_wss.on_message(None, EXAMPLE_U1))
     book_crc32 = self.book_wss.book_checksum()
     self.assertEquals(2756009329, book_crc32)
     self.assertTrue(self.book_wss.is_running)


    def test_kraken_example_r(self):

     self.loop.run_until_complete(self.book_wss.on_message(None, EXAMPLE_SNAPSHOT))
     
     self.loop.run_until_complete(self.book_wss.on_message(None, EXAMPLE_R1))

     book_crc32 = self.book_wss.book_checksum()
     self.assertEquals(2756009329, book_crc32)
     self.assertTrue(self.book_wss.is_running)
     

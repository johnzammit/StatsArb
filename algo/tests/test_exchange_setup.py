import pytest
from algo.exchange_setup import establish_connection

def test_establish_connection():
    useProd = False
    client = establish_connection(useProd=useProd)
    assert client.ping() is not None
    assert client.get_exchange_info() is not None
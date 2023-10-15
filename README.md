# Statistical Arbitrage on Cryptocurrencies


### Dependencies:

[//]: # (- `pip install -r requirements.txt`)
- `pip install python-binance`
- `pip install python-dotenv`

### Related API documentation:
- https://docs.binance.us/
- https://binance-docs.github.io/
- https://github.com/sammchardy/python-binance
- https://python-binance.readthedocs.io/en/latest/
- https://www.binance.com/en/support/faq/how-to-test-my-functions-on-binance-testnet-ab78f9a1b8824cf0a106b4229c76496d

[//]: # (- Alternative: https://github.com/binance/binance-spot-api-docs)

###  To get historical price data from Binance in the crypto_pairs_scratch.ipynb file:

- Make an account on binance.us
- Once your account is set up, follow [these steps](https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072) to create your api keys
    - In particular, make sure that you've enabled 2FA, you've made a deposit in your account, and that your account is verified
- After you have your api keys, make a file called .env at the same level as crypto_pairs_scratch.ipynb
- Your .env file should have 2 lines:
    - binanceAPIKey=YourAPIKeyThatYouCopiedFromBinance
    - binanceSecretKey=YourSecretKeyThatYouCopiedFromBinance
- Make sure to add the .env file to your gitignore
- You should now be able to run the code in crypto_pairs_scratch.ipynb (make sure that you have pip installed python-binance and python-dotenv)

### Testing your algorithm
- Enable testnet: https://www.binance.com/en/support/faq/how-to-test-my-functions-on-binance-testnet-ab78f9a1b8824cf0a106b4229c76496d
- Generate your testnet API keys and follow steps as above
- Set your .env file to have:
  - binanceAPIKey_testnet=YourAPIKeyThatYouCopiedFromBinance
  - binanceSecretKey_testnet=YourSecretKeyThatYouCopiedFromBinance
- Don't specify any `tld` in your Client initialization call
  - For production, you may specify `tld=us` if you are running the program from the US IP address
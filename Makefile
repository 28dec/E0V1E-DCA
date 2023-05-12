up:
	docker compose run --rm freqtrade backtesting --strategy-list E0V1E E0V1E_DCA --timeframe 5m -c user_data/config.json -c user_data/exchange.json --timerange 20220901- >> README.txt && cat README.txt

data:
	docker compose run --rm freqtrade download-data --timeframe 5m -c user_data/exchange.json --timerange 20200101-

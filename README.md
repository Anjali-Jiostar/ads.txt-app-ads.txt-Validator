# ads.txt / app-ads.txt Validator

Local browser app for validating ads.txt/app-ads.txt entries.

## Open in Browser

On Mac, double-click:

```text
start.command
```


The script starts the server and opens the browser automatically.

If port `8080` is already busy, it uses the next free port and prints the URL in Terminal, for example:

```text
http://localhost:8081
```

The local server fetches `https://www.hotstar.com/ads.txt` and loads it into the Current ads.txt field.

## Files

- `ads-txt-validator.html` is the validator UI.
- `server.py` serves the page and fetches Hotstar ads.txt.
- `start.command` starts the server and opens the browser on Mac.

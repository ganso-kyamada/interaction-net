# interaction_net
## headless-chrome install

```sh
curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-57/stable-headless-chromium-amazonlinux-2.zip > headless-chromium.zip
unzip headless-chromium.zip -d bin/
rm headless-chromium.zip
```

## chromedriver install

```sh
curl -SL https://chromedriver.storage.googleapis.com/95.0.4638.69/chromedriver_linux64.zip > chromedriver.zip
unzip chromedriver.zip -d bin/
chmod +x bin/chromedriver
rm chromedriver.zip
```

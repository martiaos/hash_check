This is a simple script that takes in a password suggestion, and checks if the password's MD5 or SHA-1 hash is readily available in a rainbow table.

The script uses selenium, chromium webdriver and Xlaunch in order to scrape an online look-up service. It will not work without, as the web-page results are java-script rendered and do not show up using curl or requests. 

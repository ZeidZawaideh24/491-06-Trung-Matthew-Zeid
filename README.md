# 491 Project 
## Names: Trung Tran, Matthew Hang, Zeid Zawaideh

[Download Memba](https://github.com/ZeidZawaideh24/491-06-Trung-Matthew-Zeid/releases/download/v1.0/memba.zip)

Notes: you may have to run `PowerShell -ExecutionPolicy Bypass` in PowerShell to run the script then doing `cd /path/to/memba` to folder that contains `memba.ps1`.

```powershell
# Server
./memba.ps1 --server

# Initial Memba Account setup
./memba.ps1 set_account "mail@gmail.com" "asd123";
./memba.ps1 get_account "mail@gmail.com" "asd123";

# HN Account
./memba.ps1 set_site_account 1 hackernews "<username>";
./memba.ps1 get_site_account_all 1 hackernews;

# Raindrop Account
./memba.ps1 set_site_account 1 raindrop;
./memba.ps1 get_site_account_all 1 raindrop;

# Once we got necessary IDs, we can do the following:

# Site data for site-specific configurations
./memba.ps1 set_site_data 1 hackernews 1cd282f324914f9db62b8958631551fe "{}";
./memba.ps1 set_site_data 1 raindrop 48dff44c33b14191bbf5d68c8a2dfca3 "{}";

# Set schedule
./memba.ps1 set_track 1 hackernews 1cd282f324914f9db62b8958631551fe '{\"kind\": \"interval\", \"seconds\": 15}';
./memba.ps1 set_track 1 raindrop 48dff44c33b14191bbf5d68c8a2dfca3 '{\"kind\": \"interval\", \"seconds\": 15}';
```

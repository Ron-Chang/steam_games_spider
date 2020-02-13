# pip install -r requirements.txt
source steam_spider_venv/bin/activate
git submodule init
git submodule update
cd scraping_tools
git checkout develop
cd ..

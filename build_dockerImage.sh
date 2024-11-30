cd src
docker build --platform linux/amd64 -t pica_crawler .
cd ../
docker save -o pica_crawler.tar pica_crawler
chmod 777 pica_crawler.tar
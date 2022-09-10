
rm -rf build
rm build.zip

mkdir build

pip install requests==2.28.1 -t build
cp src/* build

cp config.json build

(cd build && zip -r ../build.zip *) > /dev/null


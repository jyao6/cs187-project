
***RUN THE FOLLOWING COMMANDS IN YOUR VM TO MAKE PHARAOH WORK***

readelf -l ./pharaoh | grep ld-linux

sudo apt-get install lib32bz2-1.0
sudo apt-get install libstdc++5 libstdc++5:i386

ldd ./pharaoh (make sure none of the links say not found)
echo "filebot_postprocess.sh \"$@\""
touch -c "$1"
chmod 777 "$1"
cd /volume1/pyload/downloads
/volume1/@optware/bin/find . -iregex '.*\.url' -exec rm {} \;
/volume1/@optware/bin/find . -type d -empty -exec rmdir {} \;

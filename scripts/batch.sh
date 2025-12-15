#!/bin/bash

curl -X POST \
     -F "files=@/home/fw7th/Pictures/test.jpg" \
     -F "files=@/home/fw7th/Pictures/mobile2.jpg" \
     http://localhost:8000/predict

echo " Upload complete."


#-F "files=@/home/fw7th/Pictures/batch/file1.png" \
#-F "files=@/home/fw7th/Pictures/batch/file6.jpg" \
#-F "files=@/home/fw7th/Pictures/batch/file2.jpeg" \

#!/bin/sh

for i in *.pdf; 
do 
    echo "P R O C E S S I N G $i"; 
    pdfcrop $i $i; 

done


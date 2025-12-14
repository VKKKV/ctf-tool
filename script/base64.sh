#!/bin/bash

while IFS= read -r linea
do
   echo $linea | base64
done < $1

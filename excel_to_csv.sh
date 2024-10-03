#!/bin/bash

# Check for gnumeric package in order to convert xlsx to csv
required_package="gnumeric"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $required_package|grep "install ok installed")
echo Checking for $required_package: $PKG_OK
if [ "" = "$PKG_OK" ]; then
  echo "No $required_package. Setting up $required_package."
  sudo apt-get --yes install $required_package
fi

# Convert the xlsx to csv
ssconvert NIHMS1645237-supplement-Table_S2.xlsx identifier_table.csv

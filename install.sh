#!/bin/bash
major=`python -c 'import sys; print(sys.version_info.major)'`
minor=`python -c 'import sys; print(sys.version_info.minor)'`
if [ $major -eq 3 ] && [ $minor -ge 6 ]; then
  s="python"
else
  major=`python3 -c 'import sys; print(sys.version_info.major)'`
  minor=`python3 -c 'import sys; print(sys.version_info.minor)'`
  if [ $major -eq 3 ] && [ $minor -ge 6 ]; then
    s="python3"
  else
    echo "ERROR-- Could not find python version greater than 3.6. Exiting the installation."
    exit
  fi
fi

echo $s
if [ -z "$s" ]
then
  echo "ERROR-- Could not find python version greater than 3.6. Exiting the installation."
  exit
fi
$s setup.py install
unset NET_TEXTFSM
echo $(pwd)
export NET_TEXTFSM=$(pwd)/templates/

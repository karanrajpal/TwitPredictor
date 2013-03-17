#! /bin/bash

#read line < 'training.txt'
rm -f politictweets.txt sporttweets.txt
while read line
do
	
	#echo "$line is one line"
	echo $line > linefile.txt
	labelfield=`cut -d ' ' -f2 linefile.txt`
	#tweet=`cut -d ' ' -f2- linefile.txt`
	if [ "$labelfield" =  "Sports" ]
	then
	echo $line>> sporttweets.txt
	else
		echo $line>>politictweets.txt
		
	fi
	
done < 'training.txt'


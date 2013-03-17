import re

#Read all the required files. Read Sports tweets and politic tweets seperately. Also read in validationLines and testLines.
sportlines= open(r'sporttweets.txt', 'r').read().splitlines()
politiclines= open(r'politictweets.txt', 'r').read().splitlines()
validationLines=open(r'validation.txt', 'r').read().splitlines()
testLines=open(r'test.txt','r').read().splitlines()

#Select only the tweets from the 4 files

sportlinesSet= [line.split(' ',2) for line in sportlines]
sportlinesTrain=[row[2] for row in sportlinesSet]
politiclinesSet= [line.split(' ',2) for line in politiclines]
politiclinesTrain= [row[2] for row in politiclinesSet]
validationSet= [line.split(' ',1) for line in validationLines]
validationData=[row[1] for row in validationSet]
testSet= [line.split(' ',1) for line in testLines]
testData=[row[1] for row in testSet]
#start getStopWordList
def getStopWordList(stopWordListFileName):
    #read the stopwords
    stopWords = []
    stopWords.append('AT_USER')
    stopWords.append('URL')
    stopWords.append('RT')

    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        word.lower()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords
#end

#start getSportsWordList
def getSportsWordList(sportsWordListFileName):
    #read the stopwords
    sportsWords = []
    fp = open(sportsWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        word.lower()
        sportsWords.append(word)
        line = fp.readline()
    fp.close()
    return sportsWords
#end

#start getPoliticsWordList
def getPoliticsWordList(politicsWordListFileName):
    #read the stopwords
    politicsWords = []
    fp = open(politicsWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        word.lower()
        politicsWords.append(word)
        line = fp.readline()
    fp.close()
    return politicsWords
#end

def processTweet(tweet):
    # process the tweets
    
    #Convert to lower case
    tweet = tweet.lower()
    #Remove '
    tweet = tweet.strip('(\'s)')
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))','URL',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #strip punctuation
    tweet = tweet.strip('\?,.')
    #trim
    tweet = tweet.strip('\'"')
    return tweet
#end

stopWords = getStopWordList('stopwords.txt')
sportsWordsList = getSportsWordList('sportswords.txt')
politicsWordsList = getPoliticsWordList('politicswords.txt')
#creating the training set by attaching labels to text to form a
#list of tuples (tweet, label). Labels are 1 for sports, -1 for politics

trainset= [(x,1) for x in sportlinesTrain] + [(x,-1) for x in politiclinesTrain]

#count the number of occurrences of each word in sports and politics
sportwords={} #Dictionary stores the count for every word in sports
politicwords={} #Dictionary stores the count for every word in politics
for word in sportsWordsList:
	word = word.lower()
	sportwords[word]= sportwords.get(word, 0) + 3
for word in politicsWordsList:
	word = word.lower()
	politicwords[word]= politicwords.get(word, 0) + 3
for line,label in trainset: #for every sentence and its label
    newline = processTweet(line)
    for word in newline.split(): #for every word in the sentence
	if(word in stopWords):
            continue
	if ('#' or '@' in word):
		withoutHash = re.sub(r'#([^\s]+)', r'\1',word)
		withoutHash = re.sub(r'@([^\s]+)', r'\1',word)	
		for w in sportsWordsList:
			if (w in withoutHash): 
				sportwords[w]= sportwords.get(w, 0) + 2
				sportwords[withoutHash]= sportwords.get(withoutHash, 0) + 1
				sportwords[word]= sportwords.get(word, 0) + 2
		for m in politicsWordsList:
			if (m in withoutHash):
				politicwords[withoutHash]= politicwords.get(withoutHash, 0) + 1
				politicwords[m]= politicwords.get(m, 0) + 2
				politicwords[word]= politicwords.get(word, 0) + 2
        #Increment the count for this word based on the label
		#The .get(x, 0) method returns the current count for word x
		# and value 0 if not defined in the dictionary yet
	if label==1:
		sportwords[withoutHash]= sportwords.get(withoutHash, 0) + 1 
		
        else: politicwords[withoutHash]= politicwords.get(withoutHash, 0) + 1


#evaluate the validation data
def validateRound(i):
	for tweetid,tweet in validationSet:
    	#print(tweetid,tweet)
    		processedTweet = processTweet(tweet)	
    		totsport, totpolitic= 0.0, 0.0
    		for word in processedTweet.split():
        		if(word in stopWords):     
				continue
			if ('#' or '@' in word):
				withoutHash = re.sub(r'#([^\s]+)', r'\1',word)
				withoutHash = re.sub(r'@([^\s]+)', r'\1',word)	
				for w in sportsWordsList:
					if (w in withoutHash): 
						sportwords[w]= sportwords.get(w, 0) + 2
						sportwords[withoutHash]= sportwords.get(withoutHash, 0) + 1
						sportwords[word]= sportwords.get(word, 0) + 2
				for m in politicsWordsList:
					if (m in withoutHash):
						politicwords[withoutHash]= politicwords.get(withoutHash, 0) + 1
						politicwords[m]= politicwords.get(m, 0) + 2
						politicwords[word]= politicwords.get(word, 0) + 2
	    #Get the +1 smooth'd counts that this word occurs in each class
        #smoothing is done in case this word isnt in train set, so that there 
        #is no danger in dividing by 0 later when we do a/(a+b)
		#We are basically artifically inflating the counts by 1
        		a= sportwords.get(withoutHash,0.0) + 1.0
        		b= politicwords.get(withoutHash,0.0) + 1.0
        
        #increment our score counter for each class, based on this word
       		 	totsport+= a/(a+b)
       		 	totpolitic+= b/(a+b)
        
    #create prediction based on the counter values
    		prediction='Sports'
    		if totpolitic>totsport: 
				prediction='Politics'
		if i!=2:
    			if totsport-totpolitic>=0.5: sportwords[withoutHash]=sportwords.get(withoutHash, 0)+1 
    			elif totpolitic-totsport>=0.5: politicwords[withoutHash]= politicwords.get(withoutHash, 0) + 1
		#if i==2:
    			#print '%s %s' % (tweetid, prediction)
#end

validateRound(1)
validateRound(2)
#function defined to classify the given test file using the classifier built.
def testRound():
	for tweetid,tweet in testSet:
    		processedTweet = processTweet(tweet)	
    		totsport, totpolitic= 0.0, 0.0
    		for word in processedTweet.split():
        		if(word in stopWords):     
				continue
			if ('#' or '@' in word):
				withoutHash = re.sub(r'#([^\s]+)', r'\1',word)
				withoutHash = re.sub(r'@([^\s]+)', r'\1',word)	
#Now calculating the count for each word
        		a= sportwords.get(withoutHash,0.0) + 1.0
        		b= politicwords.get(withoutHash,0.0) + 1.0
        
        #increment our score counter for each class, based on this word
       		 	totsport+= a/(a+b)
       		 	totpolitic+= b/(a+b)
        
    #create prediction based on the counter values
    		prediction='Sports'
    		if totpolitic>totsport: 
				prediction='Politics'
    		print '%s %s' % (tweetid, prediction)
#end
testRound()
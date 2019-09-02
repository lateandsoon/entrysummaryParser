import pprint
import os

def main():
	
	def welcome():

		def choosefile():
			filelist = os.listdir()
			prunedFileList = []
			
			#remove python files from selection criteria
			for file in filelist:
				if file[-3:].upper() != '.PY':
					prunedFileList.append(file)
			
			options = []
			for option, file in enumerate(prunedFileList):
				options.append((option+1, file))

			print('Choose file to process.\n ')
			for select, filename in options:
				print(select, ':',  filename)
			target = input('\nPlease enter your desired option : ')
			try:
				target = int(target)
				return options[target-1][1]
			except:
				print('Invalid value. Please try again using an integer (1, 2, etc.). \n')
				
		print('Welcome to sendFileParse. \n\nPlease place the AE file you wish to parse in the same directory as this python file, and select it for processing.\n\n')
		print('Note this will only return the Total Duty, MPF, and HMF.\n No consideration is given to other fees and AD/CVD.\n\n')
		
		complete = False
		rejectMsg = "Invalid paramenter. Please try again using 'Y' or 'N'\n"
		while complete == False:
			target_name = choosefile()
			if os.path.isfile(str(target_name)) == True:
				content_flag = input('Do you wish to view contents? (Y/N) ').upper()
				if content_flag == 'Y' or content_flag == 'N':
					total_flag = input('Do you wish to view total values? (Y/N) ').upper()
					if total_flag == 'Y' or total_flag == 'N':
						complete = True
						return target_name, content_flag, total_flag
					else:
						print(rejectMsg)
				else:
					print(rejectMsg)
			
	def parseSendFile(target_name):
		with open(str(target_name), 'r') as send_file:
			LineItemHeader = None
			EntryLines = {}
			count = 0
			for line in send_file:

				if line[0:2] == '40':
					recordposition, CBPlineno, CO, CE = line[0:2], line[4:8], line[8:10], line[10:12]
					lineitemHeader = ('lineitemHeader', recordposition, CBPlineno, CO, CE)
					count += 1
					HTSseqCount = 1
					tariffGroupings = []
					userfeeCount = 1
					lineuserFees = []

				if line[0:2] == '50':
						recordPosition, HTS, dutyAmount, lineValue = line[0:2], line[2:12], line[13:23], line[24:34]
						tariffGrouping = ('tariffGrouping', HTSseqCount, recordPosition, ('HTS: ', HTS), ('Duty: ',dutyAmount), ('Value: ', lineValue))
						tariffGroupings.append(tariffGrouping)
						HTSseqCount +=1

				if line[0:2] == '62':
					accountclassCode, userfeeAmount = (line[2:5], line[5:13])
					lineuserFee = ('lineuserFee', userfeeCount, accountclassCode, userfeeAmount)
					lineuserFees.append(lineuserFee)
					userfeeCount+=1

				#create structure of file in dictionary
				if line[0:2] == '40':	
					try:
						EntryLines[count] = (lineitemHeader, tariffGroupings, lineuserFees)
					except:
						pass

		return EntryLines

	def contents(target_name):
		'''Presents transaction details in human readable format'''
		EntryLines = parseSendFile(target_name)
		pprint.pprint(EntryLines)

		return EntryLines

	def total(target_name):
		def minmax(totalMPF):
			'''Checks if Total MPF value meets de mimimis / maximum value and returns two value tuple (actual value, minmax val) if applicable'''
			totalMPFMax = (False, 508.70)
			totalMPFMin = (False, 26.22)

			if totalMPF > 508.70:
				totalMPFMax = (True, 508.70)
			if totalMPF < 26.22:
				totalMPFMin = (True, 26.22)

			totalMPF = (totalMPF, totalMPF)

			if totalMPFMax[0] == True:
				totalMPF = (totalMPF, totalMPFMax[1])
			if totalMPFMin[0] == True:
				totalMPF = (totalMPF[0], totalMPFMin[1])

			return totalMPF

		EntryLines = parseSendFile(target_name)
		#sum all duty lines & fees
		lineDuty = 0
		lineMPF = 0
		lineHMF = 0

		for line, value in EntryLines.items():
			#Duty
			for fees in value[1]:
				convertedDuty = int(fees[4][1])
				lineDuty += convertedDuty

			#Fees
			for fees in value[2]:
				if fees[2] == '499':
					convertedFee = int(fees[3])
					lineMPF += convertedFee

				if fees[2] == '501':
					convertedFee = int(fees[3])
					lineHMF += convertedFee

		try:
			totalMPF = lineMPF/100
			totalHMF = lineHMF/100
			totalDuty = lineDuty/100
		except:
			pass

		totalMPF = minmax(totalMPF)

		print('\nDuty:', totalDuty, 'MPF:', totalMPF[0], '(', totalMPF[1], ')', 'HMF:', totalHMF, 'Duty / MPF / HMF Total: ', totalDuty+totalMPF[1]+totalHMF)
		return EntryLines

	target_name, content_flag, total_flag = welcome()
	if content_flag == 'Y':
		contents(target_name)
	if total_flag == 'Y':
		total(target_name)

	print('Operations complete.')
	while True:
		quitquery = input('Are you done? (Y/N) ').upper()
		if quitquery == 'N':
			os.sleep(300)
		else:
			quit()
if __name__== "__main__":
   main()

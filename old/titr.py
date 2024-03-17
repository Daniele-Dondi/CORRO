#filename='log/log2024-02-28 11:59:53.301691.txt'
#filename='log/log2024-02-28 14:54:09.078966.txt'
filename='log/log2024-02-28 15:38:31.999632.txt'
filein = open(filename, 'r')
Lines = filein.readlines()
filein.close() 
count = 0
Start=False
data=[]
pH_values=[]
mL_titration=[]
# Strips the newline character
for line in Lines:
 line=line.strip()  
 if 'titration' in line:
     titration_data=line.split()
     mL=titration_data.index('mL')-1
     mL=float(titration_data[mL])
     additions=titration_data.index('additions')-1
     additions=float(titration_data[additions])
     Start=True
 if Start and not('progress') in line:
     pH=line.split(sep='\t')
     if len(pH)>4:
        data.append(float(pH[4]))
        count+=1
 if Start and 'finished' in line:
     print("pH data collected")
     break

print(mL,"mL")
print("in ",additions," additions")
print(count)
num=round(count/additions)
print(num)
fileout=open('titration3.txt',"w")
fileout.write('log/log2024-02-28 11:59:53.301691.txt\n')
fileout.write(str(mL)+"mL\n")
fileout.write("in "+str(additions)+" additions\n\n")
cnt=0
mL_added=0
for line in data:
    cnt+=1
    if (cnt==num):
        fileout.write(str(mL_added)+"\t"+str(line)+"\n")
        mL_titration.append(mL_added)
        pH_values.append(float(line))
        mL_added+=mL/additions
        cnt=0
fileout.write("\n\nFirst Derivative:\n")        
if data[count-1]>data[1]:
    find_maximum=True
    value=-1
else:
    find_maximum=False
    value=100
for i in range(len(pH_values)-1):
    deriv=(pH_values[i+1]-pH_values[i])/(mL_titration[i+1]-mL_titration[i])
    Avg_mL=(mL_titration[i+1]+mL_titration[i])/2
    fileout.write(str(Avg_mL)+"\t"+str(deriv)+"\n")
    if (find_maximum and deriv>value) or (find_maximum==False and deriv<value):
        value=deriv
        mL_equivalent_point=Avg_mL
print("equivalent point = ",mL_equivalent_point," mL")
fileout.write("\nCalculated equivalent point = "+str(mL_equivalent_point)+" mL\n")
fileout.close()    

         
     

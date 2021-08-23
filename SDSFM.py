#Imports
import sqlite3 as lite
import hashlib
import os
import random

#Define Functions
#DB
#Create Database
def createDB():
    #Create DB
    con = lite.connect("SDSFM.db")
    #Create table Encodings
    with con:
        cur = con.cursor()    
        cur.execute("CREATE TABLE Files(NameHashed TEXT, NameSalt TEXT, ContentHashed TEXT, ContentSalt TEXT)")
        
    cur.close()
    con.close()
    
#Get Data from DB
def getData():
    get_array = []
    con = lite.connect("SDSFM.db")
    with con:    
        cur = con.cursor()    
        cur.execute("SELECT * FROM Files")
        rows = cur.fetchall()

        for row in rows:
            get_array.append(row)
            #print(row)
    cur.close()
    con.close()
    
    return get_array

#ADD Data to DB
def addData(nHashed,nSalt,cHashed,cSalt):
    sqlite_insert_query = """INSERT INTO Files VALUES (?,?,?,?)"""
    
    con = lite.connect("SDSFM.db")
    con.execute(sqlite_insert_query, (nHashed,nSalt,cHashed,cSalt))
    con.commit()
    #print("Encoding inserted successfully as a BLOB into a table")
    con.close()
 
#Delete data from the DB  
def deleteData(nHashed):
    where_command = ' WHERE NameHashed ="'+ nHashed +'"'
    get_array = []
    con = lite.connect("SDSFM.db")
    with con:    
        cur = con.cursor()    
        cur.execute("DELETE FROM Files"+where_command)
        rows = cur.fetchall()
        
        for row in rows:
            get_array.append(row)
    cur.close()
    con.close()
    #print(get_array)
    
#Delete ALL data from the DB  
def deleteAllData():
    
    get_array = []
    con = lite.connect("SDSFM.db")
    with con:    
        cur = con.cursor()    
        cur.execute("DELETE FROM Files")
        rows = cur.fetchall()
        
        for row in rows:
            get_array.append(row)
    cur.close()
    con.close()
    #print(get_array)


#NON DB
# Get SHA256 of file contents
def getFileHash(filename):
    BUF_SIZE = 65536
    sha256 = hashlib.sha256()
    
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()
    
#Generate 8-char-long string for salts
def randomText(num=8):
    out = ''
    listChar = 'aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ'
    listNum = '0123456789'
    for i in range(num):
        if random.choice('01') == '1':
            out = out+ random.choice(listChar)
        else:
            out = out+ random.choice(listNum)
    return out
    
    
#Get all file in the directory of path including in subdirectory, path sould be os.getcwd()
def getAllFiles(path):
    out = []
    #print("PATH:",path)
    for root, dirs, files in os.walk(path, topdown=False):
        #print(root)
        for name in files:
            #print(os.path.join(root, name).lstrip(path))
            #print(os.path.join(root, name))
            name2= str(os.path.join(root, name))
            #print(name)
            #print(name.lstrip(str(path)))
            out.append(name2)
            #print('file',name)
            #print((root, name))
    return out
    
#createNameData is getData()
#nameData = getData()
#Check file [name] exits in the dir 
def checkfile(text,name_data):
    all_salt = []
    for e in name_data:
        all_salt.append(e[1])
    #print(all_salt)
    
    target = hashlib.sha256(text.encode('utf-8')).hexdigest()
    for e in name_data:
        for salt in all_salt:
            target2 = target+salt
            if e[0] == hashlib.sha256( target2.encode('utf-8') ).hexdigest():
                return True, e[0] , e[2] , e[3]
                # return Found, hashed name, hashed data, salt data
    return False , None , None, None
    #file not found
    
#Check the modification of file content , True = not changed
def checkContent(filename,old_hashed,old_salt):
    m2 = getFileHash(filename)
    salted2 = m2 + old_salt
    if old_hashed == hashlib.sha256(salted2.encode('utf-8')).hexdigest():
        #content not changed (same)
        return True
    else:
        return False

#Create Name Dict for file checking
def createNameDict(nameData):
    nameDict = dict()
    for e in nameData:
        nameDict[e[0]] = 'File'
    return nameDict
    
#Create Report Dict for deleted file repoting
def createReportDict(nameData):
    reportDict = dict()
    for e in nameData:
        reportDict[e[0]] = e
    return reportDict
    
#Generate data from file name. 
def generateData(filename):
    m=hashlib.sha256(filename.encode('utf-8')).hexdigest()
    salt = randomText()
    salted = m + salt
    hashed=hashlib.sha256(salted.encode('utf-8')).hexdigest()
    #out.append([hashed,salt])
    m2 = getFileHash(filename)
    salt2 = randomText()
    salted2 = m2 + salt2
    hashed2 = hashlib.sha256(salted2.encode('utf-8')).hexdigest()
    return [hashed,salt,hashed2,salt2]
    
    
#end the functions



#Start Program

#Check integrity of DB
if "SDSFM.db" not in os.listdir():
    print("Creating Database")
    print("If you running for the first time this should be ok.")
    print("If not your database is missing")
    print()
    createDB()

#Gen variables
NameData = getData()
nameDict = createNameDict(NameData)
reportDict = createReportDict(NameData)
newFileList = []
analytics = {"All":0,"Changed":0,"Deleted":0,"New":0}

#Get all files
path = os.getcwd()
allFiles = getAllFiles(path)

#Get reports
for filename in allFiles:
    result = checkfile(filename,NameData)
    if result[0] == True:
        #print("ok")
        if checkContent(filename,result[2],result[3]) == True:
            #print("Have file and same")
            nameDict[result[1]] = "Same"
        else:
            print(filename,"Changed")
            nameDict[result[1]] = "Changed"
            analytics["Changed"] += 1
    else:
        print(filename,"New")
        newFileList.append(filename)
        analytics["New"] += 1
    analytics["All"] += 1

for k,v in nameDict.items():
    if v == "File":
        print("Deleted(name,Nsalt,content,Csalt)",reportDict[k]  )
        analytics["Deleted"] += 1
   
#Clear DB
deleteAllData()

#Report
print()
print("Total",analytics["All"],"files")
if(analytics["Changed"]>0):
    print(analytics["Changed"],'files Changed')
if(analytics["New"]>0):
    print(analytics["New"],'New files')
if(analytics["Deleted"]>0):
    print(analytics["Deleted"],'files Deleted')
print()
print("Security Score:",100 - 100*(analytics["Changed"]+analytics["New"]+analytics["Deleted"])/analytics["All"])

#Regen DB
random.shuffle(allFiles)
for filename in allFiles:
    try:
        datas = generateData(filename)
        addData(datas[0],datas[1],datas[2],datas[3])
    except:
        print(filename,"Cannot be added")
        
   
   



        
        

    

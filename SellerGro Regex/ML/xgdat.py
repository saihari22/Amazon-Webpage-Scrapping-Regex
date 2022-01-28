from csv import DictReader, DictWriter
from time import time

#writecount = 0

def collectBB(bbfile,offerfile):

    blist =[]
    clist =[]
    isbb=[]
    offNo=[]
    rank=[]

    with open(bbfile,'r') as bbf, open(offerfile,'r') as cf:
        bobj = DictReader(bbf)
        cobj = DictReader(cf)
        for row in bobj:
            blist.append(row)
        for row in cobj:
            clist.append(row)

    for i,crow in enumerate(clist):
        flag = 0
        for brow in blist:
            if(brow['ASIN']==crow['ASIN']):                
                off = float(brow['No.of.Sellers'])
                if(brow['Seller']==crow['Seller']):
                    flag = 1
                else:
                    continue
        if(flag==1):
            isbb.append(1)
        else:
            isbb.append(0)
        offNo.append(off)
 
    c=1
    rank.append(c) 
    for i in xrange(1,len(clist)):
        if clist[i]['ASIN'] == clist[i-1]['ASIN']:
            c+=1
        else:
            c=1
        rank.append(c)
        
    return isbb, clist, offNo, rank


def findMin(asn,comp):

    var = []
    for x in comp:
        if x['ASIN'] == asn:
            if(x['Deliv Chg'] not in ["charges may apply","shipping calculated at checkout"]):
                var.append(float(x['Price'])+float(x['Deliv Chg']))

    mn = min(var)
    return mn

def writeTot(bbl,comp,offden, rank):

    with open("C:/Users/Kamalesh/Desktop/totaldata.csv",'a+b') as writer:
        fields = ['Diff','Ratio','Sales Rank','Seller Rating','Positive %','Feedback','FBA','Prime','Offer Density','inBB']
        obj = DictWriter(writer, fieldnames=fields)
        #global writecount
        #if writecount ==0:
         #   obj.writeheader()
        #writecount=1
        for i,row in enumerate(comp):
            if ((row['Seller Rating'] in ["No Info"]) or (row['Seller +ve %'] in ["No Info"]) or offden[i]==0.0):
                continue
            else:
                if(row['Deliv Chg'] in ["charges may apply","shipping calculated at checkout"]):
                    row['Deliv Chg'] = 0.0
                if(row['Seller Rating'] == "Just Launched"):
                   row['Seller Rating'] = 0
                if(row['Seller +ve %'] == "Just Launched"):
                   row['Seller +ve %'] = 0
                if(row['Feedback Count'] == "Just Launched"):
                   row['Feedback Count'] = 0
            
                low = findMin(row['ASIN'],comp)
                tot=float(row['Price'])+float(row['Deliv Chg'])
                diff = tot - float(low)
                ratioL = float(tot)/float(low)
                obj.writerow({'Diff':diff,'Ratio':ratioL,'Sales Rank':rank[i],'Seller Rating':float(row['Seller Rating']),'Positive %':int(row['Seller +ve %']),'Feedback':int(row['Feedback Count']),'FBA':row['FBA'],'Prime':row['Prime'],'Offer Density':float(1.0/offden[i]),'inBB':bbl[i]})

files = [] # input csv file name dates				
for x in files:
	isbb,comp,offNum,rank=collectBB("D:/data/buybox/buybox_"+x+".csv","D:/data/offers/offers_"+x+".csv")
	writeTot(isbb,comp,offNum,rank)


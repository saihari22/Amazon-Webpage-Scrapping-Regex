import re
import sys
import argparse
import json
from pprint import pprint
import os.path
import json
import csv
from itertools import imap
import xlsxwriter
from bs4 import BeautifulSoup
import unicodedata
from HTMLParser import HTMLParser
from openpyxl import Workbook
from configobj import ConfigObj
from Scrapper import clean,write_for_db,get_row_for_hist,get_row_for_seller
import time
from os import chdir, path, listdir, system, stat,getcwd


class Prod_reco(object):
    def __init__(self, marketplace_mapping_id, seller_id, domain, asin_file, html, filename):
        self.marketplace_mapping_id = marketplace_mapping_id
        self.seller_id = seller_id
        self.filename = filename
        self.regex_domain = domain
        self.asin_file = asin_file
        self.html = html
        self.asin = []
        # todo check and clear if no use
        self.value = []
        # init config paths
        self.config_path ='/home/centos/python_script/prod_reco_regex/config/'

        self.myDict = {}
        self.i = 0

    def __str__(self):
        print  self.marketplace_mapping_id
        print  self.seller_id
        print  self.domain
        print  self.asin_file
        print  self.html
        return str(self.asin_file)

    def read_config(self):
        print "self.domain", self.regex_domain
        self.config_file = os.path.join(self.config_path,'%s_regex.json'%self.regex_domain)
        return self.config_file

    def read_input(self):
        with  open(self.asin_file, "r") as file_input:
            for line in file_input:
                self.asin.append(line.replace('\n', ''))
            print self.asin


    def check_file(self):
        for i in self.asin:
            if (os.path.exists(os.path.join(self.html , i + "_M.html")) == True):
                print "Yes.Product File exists"
            if (os.path.exists(self.html + i + "_fba.html") == True):
                print "Competitors exist"

    def apply_regex(self, regex_list, content):
        for regex in regex_list:
            try:
                res = re.findall(regex, content)
                if (''.join(res) != ''):
                    return ' AND '.join(res)
            except Exception, e:
                print e,"error in apply regex",regex
                return "No Info"
        return "No Info"

    def gather_data(self):
        '''
        gather all fuelds
        :return:
        '''
        try:
            for count, i in enumerate(self.asin):
                print "processing {}th asin {}".format(count,i)
                prod_file = self.html + i + "_M.html"
                slr_file = self.html + i + "_fba.html"
                condn1 = os.path.exists(prod_file) and os.path.exists(slr_file)
                if condn1 : 
                    condn2 = (stat(prod_file).st_size>110000) and (stat(slr_file).st_size>80000)
                    if condn2 :
                        self.myDict[i] = {}
                        file_html = open(self.html + i + "_M.html", "r")
                        html_content = file_html.read()
                        for k,val in json.load(open(self.config_file)).iteritems():
                            #print "getting",k
                            if val != "":
                                if k == 'fba':
                                     fba_html = open(self.html + i + "_fba.html", "r")
                                     fba_html_content = fba_html.read()
                                     self.myDict[i][k] = clean(self.normalize_fba_op(val,fba_html_content))
                                elif k == 'author':
                                     self.myDict[i][k] = clean(self.normalize_author_op(val,html_content))
                                elif k == 'total_sellers':
                                     reg = val[:]
                                     reg = [ r.replace('@ASIN',i)  for r in reg ]      
                                     self.myDict[i][k] = clean(self.apply_regex(reg,html_content))
                                elif k == 'buybox_type':
                                     self.myDict[i][k] = clean(self.get_bb_type(i,val,html_content))
				elif k=='is_amazon_a_seller':
				     as_html = open(self.html + i + "_fba.html", "r")
                                     as_html_content = as_html.read()
				     self.myDict[i][k]=clean(self.get_amazon_seller(val,as_html_content))	
                                else:
                                    self.myDict[i][k] = clean(self.apply_regex(val,html_content))
                            else:
                                self.myDict[i][k] = "No Info"
                    else :
                         print "corrupted file"
                         continue
                else:
                    print "Prod file or Seller file missing"
                    continue
                #write csv here   
                self.export_data_csv(self.myDict[i],i)
               # pprint(self.myDict)
        except Exception,e:
            print "error is ",e,"regex prob?","k=",k


    def normalize_author_op(self, regex_list, content):
        for regex in regex_list:
            try:
                res = re.findall(regex, content)
                if res == []:
                    return 'No info'
                else:
                    b=[i for sub in res for i in sub]
                    c=[y for y in b if y is not '']
                    return ' AND '.join(c)
            except Exception, e:
                print e,"author error"
                return "No Info"



    def normalize_fba_op(self, regex_list, content):
        self.i_time = 1
        output = None
        for regex in regex_list:
            try:
                res = re.findall(regex, content)
                
                # print "{} - {}".format(regex, res)
                if (res ==[]):
                    if self.i_time ==1:
                        self.i_time+=1                       
                        #output =  'AND'.join(res)
                    else:
                        return "0"
                else:
                        if self.i_time ==1:
                            if ''.join(res) != '':
                                 page=int(res[0])*10
				 return str(page)
                         #        return ''.join(res)
                        else:
                            b=[i for sub in res for i in sub]
                            c=[y for y in b if y is not '']
                            d = [slr for slr in c  if slr.strip() != 'PanWorld Books']
                            return str(len(d))
            except Exception, e:
                print e,"fba error"
                return "No Info"


    def get_bb_type(self,asin, regex_list, content):
        bb_type = None
        for regex in regex_list:
            try:
                res = re.findall(regex, content)
                if (''.join(res) != ''):
                    bb_type =  ' AND '.join(res)
		    return bb_type
                else:
                    bb_type ="No Info"
            except Exception, e:
                print e,"error in apply regex",regex
                bb_type =  "No Info"
	if (bb_type=="No Info"):
            if(self.myDict[asin]["buybox_price"]!="No Info"):
    	        if(self.myDict[asin]["total_sellers"]>0):
		    return "New"
		else:
		    return "Used"
	    else:
		return "No Info"	
	else :
	    return bb_type

    def get_amazon_seller(self,regex_list,content):

        amazon_seller=self.apply_regex(regex_list, content)
	if(amazon_seller=="No Info"):
		return 'No'
	else:
		return 'Yes'

    def export_data_excel(self):
        # workbook  = xlsxwriter.Workbook('filename.xlsx')
        # worksheet = workbook.add_worksheet()
        wb = Workbook()
        ws1 = wb.active
        i = 0
        for asin, data in self.myDict.iteritems():
            if i == 0:
                row = data.keys()
            else:
                row = data.values()
            ws1.append(row)
            # for key in d:
            i += 1
        wb.save(self.filename)
        # workbook.close()
        print "Excel generated"

    def my_cpy(self,dic, **kwargs):
        new_d = dic.copy()
        # print kwargs
        new_d.update(kwargs)
        return new_d
    
    def my_reduce_opposite_mul_keys(self, keys, dic):
        vals = {}
        n_times = None
        for key in keys:
            n_times = len(dic[key].split('AND'))
            vals[key] = dic[key].split('AND')
            #print n_times
            #sys.exit()
        for i in range(n_times):
            inst = None
            #print i
            #print dict(zip(keys, [vals[x][i] for x in keys]))
            inst = self.my_cpy(dic, **dict(zip(keys, [vals[x][i] for x in keys])))
            # print inst
            # print type(inst)
            # print id(inst)
    
            #print "updated", inst
            yield inst
    


    def write_for_panworld(self,data_dict,asin):
        data_dict.update({"asin":asin})
        temp =  write_for_db(data_dict,asin)
        with open('file_uk_17k.csv', "a") as f:
            if self.i ==0:
                header =self. get_row(temp.keys())
                f.write(header)
            row = self.get_row(temp.values())
            f.write(row)
            self.i+=1

    def export_data_csv(self,data_dict,asin):
        data_dict.update({"asin":asin})
        #write to send as excel        
        self.write_for_panworld(data_dict,asin)
        keys = ['category', 'sub_cat_sales_rank', 'mp_cat_id']        
        my_encoded = []
        i = 0
        for x in self.my_reduce_opposite_mul_keys( keys, data_dict):
            temp = x
            #print "here", x
            #print x in my_encoded
            #print "apend", x
            #print "before encode", my_encoded
            my_encoded.append(temp)
            if i == 0:
                a = x
                #print a
            else:
                #print "a bfore b", a
                b = x
                #print "b", b
            i += 1
            #print "encoded", my_encoded
        for data in my_encoded:
            hist_row = get_row_for_hist(data)
            with open('hist_data_uk_17k.csv','a') as h:
                h.write(hist_row)  
            slr_row = get_row_for_seller(data,self.seller_id,self.marketplace_mapping_id)
            with open('slr_data_uk_17k.csv','a') as h:
                    h.write(slr_row)  

    def get_row(self,data_lis):
        delimtr = '\t'
        return  delimtr.join(['"'+str(data)+'"' for data in data_lis])+'\n'

    def update(self):
        '''
         write my dict data in order to insert in table
        '''
        for i in self.asin:
            self.myDict[i]["mp_pin"] = self.marketplace_mapping_id
            self.myDict[i]["sync_id"] = '123'
            self.myDict[i]["brand"] = ''
            self.myDict[i]["buybox_seller"] = ''
            self.myDict[i]["price_and_shipping"] = ''
            self.myDict[i]["buybox_mp_fulfilled"] = ''
            self.myDict[i]["last_modified_date"] = ''
            self.myDict[i]["crawl_date"] = ''
            self.myDict[i]["last_modified_by"] = ''
            self.myDict[i]["amazon_url"] = ''
            self.myDict[i]["item_or_shipping_weight"] = ''
            self.myDict[i]["competitor_1_name"] = ''
            self.myDict[i]["competitor_2_name"] = ''
            self.myDict[i]["competitor_3_name"] = ''
            self.myDict[i]["competitor_1_price"] = ''
            self.myDict[i]["competitor_2_price"] = ''
            self.myDict[i]["competitor_3_price"] = ''
            self.myDict[i]["competitor_1_shipping_price"] = ''
            self.myDict[i]["competitor_2_shipping_price"] = ''
            self.myDict[i]["competitor_3_shipping_price"] = ''
            self.myDict[i]["price_difference_with_competitor_1"] = ''
            self.myDict[i]["price_difference_with_competitor_2"] = ''
            self.myDict[i]["price_difference_with_competitor_3"] = ''
            self.myDict[i]["am_I_in_top_3"] = ''
            self.myDict[i]["am_I_out_of_stock"] = ''
            self.myDict[i]["my_price"] = ''
        self.export_data_csv()
        print "Data updated"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-mid', '--mid', action="store", type=int, dest="Mapping_Id")
    parser.add_argument('-dom', '--dom', action="store", dest="Domain", required='True')
    parser.add_argument('-sell', '--sell', dest="seller_id", type=int, )
    parser.add_argument('-asin', '--asin', dest="asin", required='True')
    parser.add_argument('-html', '--html', dest="html_path", required='True')
    parser.add_argument('-file', '--file', dest="filename")
    results = parser.parse_args()
    reco = Prod_reco(results.Mapping_Id,  results.seller_id, results.Domain , results.asin, results.html_path,
                     results.filename)
    # print reco
    reco.read_input()
    # reco.check_file()
    reco.read_config()
    reco.gather_data()

    if (results.Mapping_Id == 234 and results.seller_id == 224):
        #reco.update()
        pass
    else:
        reco.export_data_excel()


if __name__ == '__main__':
    main()

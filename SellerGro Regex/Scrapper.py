from HTMLParser import HTMLParser
import re
import unicodedata
from time import strftime,gmtime
from Database_connection import Database
import sys
db_con = Database()

def clean(data):
    #clean html entities
	#data=data.encode('utf-8')
    data=clean_html(data)
    data=clean_unicode(data)
    data=clean_html_tags(data)
    data=clean_pound(data)
    data=cleanspanish(data)
    return data.strip()


def clean_html(data):
    data=HTMLParser().unescape(data)
    #data=data.replace('\xc3\xb1','n')
    return data
def clean_unicode(data):
     #value=data.encode('utf-8').strip()
   # value =unicode(data,'UTF-8')
    #data= data.replace('\xa0',' ')
     #data= data.replace('\xc2\xa3','')
    if type(data) == unicode:
         data=data.encode('utf-8')
    return str(data)

def clean_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)
def clean_pound(data):
    return data.replace('\xc2\xa3','')
def cleanspanish(data):
    return data.replace('\xc3\xb1','')    
def write_for_db(orig_data,asin,map_id = 234, sync_id = 398769):
    orig_data["mp_pin"]=asin		 
    orig_data["sync_id"]=sync_id
    orig_data["brand"]=''
    orig_data["buybox_seller"]=''
    orig_data["price_and_shipping"]=''
    orig_data["buybox_mp_fulfilled"]=''
    orig_data["last_modified_date"]=strftime("%Y-%m-%d %H:%M:%S")
    orig_data["crawl_date"]=strftime("%Y-%m-%d %H:%M:%S")
    orig_data["last_modified_by"]=''
    orig_data["amazon_url"]=''
    orig_data["item_or_shipping_weight"]=''
    orig_data["competitor_1_name"]=''
    orig_data["competitor_2_name"]=''
    orig_data["competitor_3_name"]=''
    orig_data["competitor_1_price"]=''
    orig_data["competitor_2_price"]=''
    orig_data["competitor_3_price"]=''
    orig_data["competitor_1_shipping_price"]=''
    orig_data["competitor_2_shipping_price"]=''
    orig_data["competitor_3_shipping_price"]=''
    orig_data["price_difference_with_competitor_1"]=''
    orig_data["price_difference_with_competitor_2"]=''
    orig_data["price_difference_with_competitor_3"]=''
    orig_data["am_I_in_top_3"]=''
    orig_data["am_I_out_of_stock"]=''
    orig_data["my_price"]=''
    return orig_data 

def bulk_upload(table,file_path,env = "test"):
        '''
        write the mkp_seller_id file into marketplace_seller_id table in the database
        :return:
        '''
        try:
            db = Database()
            query = " LOAD DATA LOCAL INFILE  '" + file_path + "' INTO TABLE " + table + " FIELDS TERMINATED BY ',' " \
                                                                           "ENCLOSED BY '\"' LINES TERMINATED BY '\n' "
            print "bulk upload %s"%query
            res = db.update(query)
            print "result = %s"%res
            return res
        except Exception, e:
            print e

def get_row_for_hist(data):
    order = [
                "mp_cat_id",
                "mp_pin",
                "sync_id",
                "title",
                "isbn_13",
                "brand",
                "buybox_seller",
                "buybox_price",
                "buybox_shipping",
                "price_and_shipping",
                "rrp",
                "sales_rank",
                "total_sellers",
                "fba",
                "buybox_mp_fulfilled",
                "last_modified_date",
                "crawl_date",
                "last_modified_by",
                "amazon_url",
                "buybox_type",
                "product_description",
                "img_url",
                "item_weight",
                "item_weight_or_shipping_weight",
                "width",
                "length",
                "breadth",
                "binding",
                "author",
                "publisher",
                "publish_year",
                "edition",
                "competitor_1_name",
                "competitor_1_price",
                "competitor_1_shipping_price",
                "competitor_2_name",
                "competitor_2_price",
                "competitor_2_shipping_price",
                "competitor_3_name",
                "competitor_3_price",
                "competitor_3_shipping_price",
                "price_difference_with_competitor_1",
                "price_difference_with_competitor_2",
                "price_difference_with_competitor_3",
                "am_I_in_top3",
                "am_I_out_of_stock",
                "my_price",
                "sub_cat_sales_rank",
                "domain"
              ]
    values = [] 
    for d in order:
         if d !='buybox_shipping':
             values.append(data.get(d,'No Info'))
         else:
           temp = data.get(d,'No info')
           if (('Free' in temp) or('free' in temp) or ('FREE' in temp)):
                temp = '0.0'
           values.append(temp)
    delimtr = '\t'
    return  delimtr.join(['"'+str(val)+'"' for val in values])+'\n'

def get_row_for_seller(data,seller_id,marketplace_mapping_id):
    order = [
                "mp_cat_id",
                "mp_pin",
                "seller_id",
                "marketplace_mapping_id",
                "sync_id",
                "title",
                "isbn_13",
                "brand",
                "buybox_seller",
                "buybox_price",
                "buybox_shipping",
                "price_and_shipping",
                "rrp",
                "sales_rank",
                "total_sellers",
                "fba",
                "buybox_mp_fulfilled",
                "last_modified_date",
                "crawl_date",
                "last_modified_by",
                "amazon_url",
                "buybox_type",
                "product_description",
                "img_url",
                "item_weight",
                "item_weight_or_shipping_weight",
                "width",
                "length",
                "breadth",
                "binding",
                "author",
                "publisher",
                "publish_year",
                "edition",
                "competitor_1_name",
                "competitor_1_price",
                "competitor_1_shipping_price",
                "competitor_2_name",
                "competitor_2_price",
                "competitor_2_shipping_price",
                "competitor_3_name",
                "competitor_3_price",
                "competitor_3_shipping_price",
                "price_difference_with_competitor_1",
                "price_difference_with_competitor_2",
                "price_difference_with_competitor_3",
                "am_I_in_top3",
                "am_I_out_of_stock",
                "my_price",
                "sub_cat_sales_rank",
                "domain"
              ]
    values = [] 
    for d in order:

         if d !='buybox_shipping':
             if d == 'seller_id':
                values.append(seller_id) 
             elif d == 'marketplace_mapping_id':
                values.append(marketplace_mapping_id) 
             else:
                 values.append(data.get(d,'No Info'))
         else:
           temp = data.get(d,'No info')
           if (('Free' in temp) or('free' in temp) or ('FREE' in temp)):
                temp = '0.0'
           values.append(temp)
    delimtr = '\t'
    return  delimtr.join(['"'+str(val)+'"' for val in values])+'\n'


def get_sync_id(marketplace_mapping_id,comment,marketplace_id = 1,sync_type_id=17):
    sync_currenttime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    sync_entry_query="""INSERT into sync_details(marketplace_mapping_id,mp_id,sync_type_id,sync_start_time,comment,sync_type,syn_status_id)values ({},{},{},"{}","{}",{},{})""".format(marketplace_mapping_id,marketplace_id,sync_type_id,sync_currenttime,comment,1,1)
     #print "sync_entry_query = ",sync_entry_query
    sync_id = db_con.insert_query(sync_entry_query)
    return sync_id                 

def bulk_upload(self,table,file_path,env = "test"):
    '''
    write the mkp_seller_id file into marketplace_seller_id table in the database
    :return:
    '''
    try:
        db = Database()
        query = " LOAD DATA LOCAL INFILE  '" + file_path + "' INTO TABLE " + table + " FIELDS TERMINATED BY ',' " \
                                                                        "ENCLOSED BY '\"' LINES TERMINATED BY '\n' "
        res = db_con.update(query)
        return res
    except Exception, e:
        print e



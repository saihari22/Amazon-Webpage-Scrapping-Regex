from ProdReco import Prod_reco
obj =  Prod_reco(234, 224, 'UK' , 'my_file.txt', '/','my_file.csv')
#regex =["""<h3 class="a-spacing-none olpSellerName">\s+<img alt="([A-Z a-z.]+)|<h3 class="a-spacing-none olpSellerName">[\s<>a-z="-/_&%0-9?;:A-Z'^ ]+">([A-Z a-z&-]+)</a>"""] 
regex = ["""</span>([0-9]*)<span class = "aok-offscreen"></span></a></li>\s+<li class="a-last">""","""<h3 class="a-spacing-none olpSellerName">\s+<img alt="([A-Z a-z.]+)|<h3 class="a-spacing-none olpSellerName">[\s<>a-z="-/_&%0-9?;:A-Z'^ ]+">([A-Z a-z&-]+)</a>"""]
def test_zero_sellers():
     f = 'fba_templates/empty.html'
     with open(f,'r') as htm:
        res= obj.normalize_fba_op(regex,htm.read())
        print "test_zero_sellers",res
        #assert res == 0
        

def test_take_from_pagination():
     f = 'fba_templates/both.html'
     with open(f,'r') as htm:
        res= obj.normalize_fba_op(regex,htm.read())
        print "test_take_from_pagination",res
        #assert res == 0

def take_from_my_page():
     f = 'fba_templates/single.html'
     with open(f,'r') as htm:
        res= obj.normalize_fba_op(regex,htm.read())
        print "take_from_my_page",res
        #assert res == 0

zero_test = test_zero_sellers()
pg = test_take_from_pagination()
first_page = take_from_my_page()

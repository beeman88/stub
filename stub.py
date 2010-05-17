from bottle import route, run, request, response

# globals
# global in_progress_count 
# global in_progress_reqs 
# global new_link_ids_index 
# global new_link_ids
global debug
global log
global port_number
global TRADING_ACCOUNTS
global SALES_INVOICES 

@route('/')
def index():
    return '''
<h3>This test will send the responses to synchronize new customers, invoices from billing boss to simply accounting.</h3>
<br/>
<ul>
<li>Instructions:</li>
<li>1. The port number global set in stub.py is the name of a folder that has xml files that contain responses</li>
<li>2. The xml files are copied to a new folder and modified for each test cases</li>
<li>3.</li>
<li>4.</li>
</ul>
'''

# 1. Authentication request. (includes username and password)
# - GET request
# - On success return 200 OK
# - On failure return 401 Not Authorized
@route('/sdata/billingboss/crmErp/-')
def index():
    log_method_start('Authentication')
    return authentication()

# 2. Get Count of linked customers, invoices
#    Return 0 linked resources
# GET request
# /sdata/billingboss/crmErp/TradingAccounts/$linked?count=0
# TODO because no tradingAccount entries are returned, the link for first, last, next page have count = 0
# compare with Sage 50 - Act! implementation
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$linked', method='GET')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$linked', method='GET')
def index():
    log_method_start('Count of linked resources')
    if authentication() <> "Authenticated":
        return "Access Denied"    
                 
    try:
        count = request.GET['count']
    except Exception:
        if debug == "1":
            write_to_log('count does not exist')
        return
    else:
        if debug == "1":
            write_to_log('count = {0}'.format(count))
            write_to_log('return count linked resources')
        response.content_type='application/atom+xml'    
        return sdata_link_count_linked()

# GET requests  
# 3a. Get count of all customers, invoices
# /sdata/billingboss/crmErp/-/tradingAccounts?count=0

# TODO /sdata/billingboss/crmErp/-/tradingAccounts?select=name,customerSupplierFlag the real request?
# /sdata/billingboss/crmErp/-/tradingAccounts
# all customers, invoices
@route('/sdata/billingboss/crmErp/-/tradingAccounts', method='GET')
@route('/sdata/billingboss/crmErp/-/salesInvoices', method='GET')
def index():
    log_method_start('GET count of all resources or link feed')
    if authentication() <> "Authenticated":
        return "Access Denied"

    response.content_type='application/atom+xml'

    # when count parameter exists, return count of all resources
    try:
        count = request.GET['count']
    except Exception:
        if debug == "1":
            write_to_log('count does not exist')
    else:
        if debug == "1":        
            write_to_log('count = {0}'.format(count))
            write_to_log('return count of all resources')
        return sdata_link_count_all()

    # return feed of resources
    # the select parameter specifies what fields to return is handled in the xml file
    return sdata_link_feed_all()

# 5. Post new links
# POST request
# response is one entry for Ashburton Reinforcing
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$linked', method='POST')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$linked', method='POST')
def index():
    log_method_start('Post new links')

    if authentication() <> "Authenticated":
        return "Access Denied"

    body = request.body.read()
    write_to_log(body)        
    if request.url.find(TRADING_ACCOUNTS) > 0:
        return post_link_resource(TRADING_ACCOUNTS, body)
    elif request.url.find(SALES_INVOICES) > 0: 
        return post_link_resource(SALES_INVOICES, body)
    else:
        response.status = 404
        write_to_log("Exception")
        return sdata_link_post_from_file()

# 6. Create sync request
# POST
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$syncSource', method='POST')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$syncSource', method='POST')
def index():
    log_method_start('Create sync request')

    if authentication() <> "Authenticated":
        return "Access Denied"    

    try:
        trackingId = request.GET['trackingId']
    except Exception:
        if debug == "1":
            write_to_log('trackingId does not exist')
        return
    else:
        if debug == "1":        
            write_to_log('trackingId = {0}'.format(trackingId))

    # TODO don't know why these parameters are not in request
##    try:
##        runName = request.GET['runName']
##    except Exception:
##        write_to_log('runName does not exist')
##        return
##    else:
##        write_to_log('runName = {0}'.format(runName))
##
##    try:
##        runStamp = request.GET['runStamp']
##    except Exception:
##        write_to_log('runStamp does not exist')
##        return
##    else:
##        write_to_log('runStamp = {0}'.format(runStamp))

    write_to_log('202 Accepted')
    response.status = 202
    response.content_type='application/xml'
    response.headers['Location'] = 'http://localhost:{0}'.format(port_number) + request.path + "('" + trackingId + "')"
    return sdata_sync_accepted()

# First request return sync in progress, second request returns feed
# 7a. Request status of sync request (In progress)
# 7b. Request status of sync request (Complete)
# GET on location of previous request
# /sdata/billingboss/crmErp/-/tradingAccounts/$syncSource('abc42b0d-d110-4f5c-ac79-d3aa11bd20cb')
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$syncSource('':tracking_id'')', method='GET')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$syncSource('':tracking_id'')', method='GET')
def index(tracking_id):
    global in_progress_count 
    global in_progress_reqs    
    log_method_start('Request status of sync')

    if authentication() <> "Authenticated":
        return "Access Denied"
    
    if debug == "1":
        write_to_log('tracking id = {0}'.format(tracking_id))
        write_to_log('in_progress_count = {0}'.format(in_progress_count))

    if in_progress_count < in_progress_reqs:
        if debug == "1":        
            write_to_log('sync feed in progress')
        in_progress_count = in_progress_count + 1
        response.status = 202
        response.content_type='application/xml'
        response.headers['Location'] = request.url
        return sdata_sync_in_progress()
    else:
        if debug == "1":        
            write_to_log('sync feed complete')        
        in_progress_count = 0
        response.status = 200
        response.content_type='application/atom+xml'
        response.headers['Location'] = request.url
        return sdata_sync_feed()

# 8. Delete (finish) sync request
# DELETE request
# /sdata/billingboss/crmErp/-/tradingAccounts/$syncSource('abc42b0d-d110-4f5c-ac79-d3aa11bd20cb')
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$syncSource('':tracking_id'')', method='DELETE')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$syncSource('':tracking_id'')', method='DELETE')
def index(tracking_id):
    log_method_start('Delete (finish) sync request')

    if authentication() <> "Authenticated":
        return "Access Denied"
    
    if debug == "1":
        write_to_log('tracking id = {0}'.format(tracking_id))
    response.status = 200
    return "DELETED"

##################################################

def sdata_link_count_linked():
    return read_file('link_count_linked.xml')

def sdata_link_count_all():
    return read_file('link_count_all.xml')

def sdata_link_feed_unlinked():
    return read_file('link_feed_unlinked.xml')

def sdata_link_feed_all():
    return read_file('link_feed_all.xml')

def sdata_link_post_from_file():
    return read_file('link_post.xml')

def post_link_resource(resource_type, body):
    import xml.dom.minidom        
    # create an xml document from the request body
    
    doc = xml.dom.minidom.parseString(body)
    write_to_log(doc.toxml())

    try:
        # set response status and content
        response.status = 201
        response.content_type='application/atom+xml'

        # get url, uuid, key, name from xml doc
        payload = doc.getElementsByTagName("payload")[0]
        write_to_log(payload.toxml())
        xml = ''
        if resource_type == TRADING_ACCOUNTS:
            resource = payload.getElementsByTagName("crm:tradingAccount")[0]
            
            uuid = get_uuid_from_resource(resource)
            set_response_location(uuid)
            url = get_url_from_resource(resource)
            key = get_key_from_resource(resource)
            name = get_name_from_payload(payload)

            xml = sdata_link_post_tradingAccount(url, key, uuid, name)
            
        elif resource_type == SALES_INVOICES:
            resource = payload.getElementsByTagName("crm:salesInvoice")[0]
            
            uuid = get_uuid_from_resource(resource)
            set_response_location(uuid)            

            url = get_url_from_resource(resource)             
            key = get_key_from_resource(resource)
            #customer reference            
            ref = get_ref_from_payload(payload)            

            elCust = payload.getElementsByTagName("crm:tradingAccount")[0]
            cust_uuid = get_uuid_from_resource(elCust)
            cust_key = get_key_from_resource(elCust)
            
            xml = sdata_link_post_salesInvoice(url, key, ref, cust_key, cust_uuid)

        doc.unlink()            
        write_to_log(xml)
        return xml        
    except Exception:
        doc.unlink()
        response.status = 404
        write_to_log("Exception")
        return sdata_link_post_from_file()

def get_uuid_from_resource(resource):
    write_to_log(resource.toxml())        
    uuid = resource.attributes["sdata:uuid"].value
    write_to_log(uuid)
    return uuid

def get_url_from_resource(resource):
    url = resource.attributes["sdata:url"].value
    return url

def get_key_from_resource(resource):
    url = resource.attributes["sdata:url"].value
    write_to_log(url)
    # get the key from the url between the ('...') TODO use regex
    key = url[url.index("('") + 2:url.index("')")]
    write_to_log(key)
    return key

def get_name_from_payload(payload):
    elName = payload.getElementsByTagName("crm:name")[0]
    write_to_log(elName.toxml())
    name = elName.firstChild.data
    write_to_log(name)
    return name

def get_ref_from_payload(payload):
    elRef = payload.getElementsByTagName("crm:customerReference")[0]
    write_to_log(elRef.toxml())
    ref = elRef.firstChild.data
    write_to_log(ref)
    return ref

def set_response_location(uuid):
    response.headers['Location'] = 'http://localhost:{0}'.format(port_number) + request.path + "('" + uuid + "')"                

def sdata_link_post_tradingAccount(url, key, uuid, name):
    return '''
    <entry xmlns:xs="http://www.w3.org/2001/XMLSchema" 
           xmlns:cf="http://www.microsoft.com/schemas/rss/core/2005" 
           xmlns="http://www.w3.org/2005/Atom" 
           xmlns:sdata="http://schemas.sage.com/sdata/2008/1" 
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
           xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" 
           xmlns:sme="http://schemas.sage.com/sdata/sme/2007" 
           xmlns:http="http://schemas.sage.com/sdata/http/2008/1" 
           xmlns:sc="http://schemas.sage.com/sc/2009" 
           xmlns:crm="http://schemas.sage.com/crmErp/2008" >
      <id>http://www.billingboss.com/sdata/billingboss/crmErp/-/tradingAccounts/$linked('{2}')</id>
      <title>Linked account {2}</title>
      <updated>2010-05-25T13:27:19.207Z</updated>
      <payload xmlns="http://schemas.sage.com/sdata/2008/1">
        <crm:tradingAccount sdata:uuid="{2}"
          sdata:url="{0}"
          sdata:key="{1}" 
          xmlns="http://schemas.sage.com/crmErp">
          <crm:name>{3}</crm:name>
        </crm:tradingAccount>
      </payload>
    </entry>
    '''.format(url, key, uuid, name)

def sdata_link_post_salesInvoice(key, uuid, reference, cust_key, cust_uuid):
    return '''
    <entry xmlns:xs="http://www.w3.org/2001/XMLSchema" 
           xmlns:cf="http://www.microsoft.com/schemas/rss/core/2005" 
           xmlns="http://www.w3.org/2005/Atom" 
           xmlns:sdata="http://schemas.sage.com/sdata/2008/1" 
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
           xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" 
           xmlns:sme="http://schemas.sage.com/sdata/sme/2007" 
           xmlns:http="http://schemas.sage.com/sdata/http/2008/1" 
           xmlns:sc="http://schemas.sage.com/sc/2009" 
           xmlns:crm="http://schemas.sage.com/crmErp/2008" >
      <id>http://www.billingboss.com/sdata/billingboss/crmErp/-/salesInvoices/$linked('{1}')</id>
      <title>Linked invoice {1}</title>
      <updated>2010-05-25T13:27:19.207Z</updated>
      <payload xmlns="http://schemas.sage.com/sdata/2008/1">
        <crm:salesInvoice sdata:uuid="{1}"
          sdata:url="http://www.billingboss.com/sdata/billingboss/crmErp/-/salesInvoices('{0}')"
          sdata:key="{0}" 
          xmlns="http://schemas.sage.com/crmErp">
                    <crm:tradingAccount sdata:url="http://www.billingboss.com/sdata/billingboss/crmErp/-/tradingAccounts('{3}')" sdata:uuid="{4}" />
                    <crm:customerReference>{2}</crm:customerReference>
        </crm:salesInvoice>
      </payload>
    </entry>
    '''.format(key, uuid, reference, cust_key, cust_uuid)    
    
def sdata_sync_accepted():
    return read_file('sync_accepted.xml')

def sdata_sync_in_progress():
    return read_file('sync_in_progress.xml')

# TODO What is the simply endpoint?
def sdata_sync_feed():
    return read_file('sync_feed.xml')

def read_file(filename):
    import os.path

    if debug == "1":
        write_to_log('read file {0}'.format(filename))    
        write_to_log('port = {0}'.format(port_number))
    path_filename = os.path.join(str(port_number), filename)
    if debug == "1":
        write_to_log('path and filename = {0}'.format(path_filename))
    f = open(path_filename, 'r')
    print f
    xml = f.read()
    write_to_log(xml)
    f.close()
    return xml

def debug_write_to_log(line):
    if debug == "1":
        write_to_log(line)

def write_to_log(line):
    log.write(line + '\n')

def log_method_start(str):
    write_to_log('')
    if debug == "1":
        write_to_log(str)
    write_to_log(request.url)

def authentication():
    if not request.auth:
        if debug == "1":
            write_to_log('401 Not authenticated')
        response.status = 401
        return "Access denied."

    if debug == "1":
        write_to_log('200 OK')
    response.status = 200
    return "Authenticated"


# bottom

# input port number
import csv
import os.path
port_number = raw_input("Enter port number == folder where xml responses stored: ")

# open log file
log_filename = os.path.join(str(port_number), 'log.txt')
log = open(log_filename, 'w')

config_filename = os.path.join(str(port_number), 'config.csv')
config = open(config_filename, 'r')

#read sync trackingId from config.csv
tracking_id = config.readline()
write_to_log('sync tracking id = {0}'.format(tracking_id))
#read new link uuid from config.csv
new_link_line = config.readline()
new_link_ids = new_link_line.split(',')
write_to_log('new link ids = {0}'.format(new_link_ids))

# initialize
new_link_ids_index = 0
in_progress_count = 0
in_progress_reqs = 1
TRADING_ACCOUNTS = "tradingAccounts"
SALES_INVOICES = "salesInvoices"

#read debug flag
debug = config.readline()
write_to_log('debug = {0}'.format(debug))

run(host='localhost', port=port_number)


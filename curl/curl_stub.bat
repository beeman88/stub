echo off

IF "%1"=="" (
echo "usage: curl_stub port trackingId user password resource"
echo "curl_stub 8080 abc42b0d-d110-4f5c-ac79-d3aa11bd20cb user password tradingAccounts(salesInvoices)"
GOTO :EOF
)

IF "%2"=="" (
echo "usage: curl_stub port trackingId user password resource"
echo "curl_stub 8080 abc42b0d-d110-4f5c-ac79-d3aa11bd20cb user password tradingAccounts(salesInvoices)"
GOTO :EOF
)

IF "%5"=="" (
echo "usage: curl_stub port trackingId user password resource"
echo "curl_stub 8080 abc42b0d-d110-4f5c-ac79-d3aa11bd20cb user password tradingAccounts(salesInvoices)"
GOTO :EOF
)


IF "%5"=="%5" set select="name,customerSupplierFlag"
IF "%5"=="salesInvoices" set select="tradingAccount,customerReference"

IF "%1"=="8090" GOTO 8090
IF "%1"=="8095" GOTO 8095
IF "%1"=="9050" GOTO 9050


REM authorization fail 401
curl -v http://localhost:%1/sdata/billingboss/crmErp/-

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-

REM get count linked customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked?count=0

REM get count all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?count=0

REM don't get unlinked customers
REM get unlinked customers
REM curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?where=uuid+eq+null&select=%select%

REM get all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?select=%select%

REM post customer new links
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload/></entry>" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked

REM create sync request
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload><digest/></payload></entry>" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource?trackingId=%2&runName=%5&runStamp=2010-10-14T08:51:02

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

GOTO EOF


:8090

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-

REM get count linked customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked?count=0

REM get count all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?count=0

REM get all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?select=name,customerSupplierFlag

REM post 2 customer new links
curl -v -u%3:%4 -X POST http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked

REM create sync request
curl -v -u%3:%4 -X POST http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource?trackingId=%2&runName=customers&runStamp=2010-10-14T08:51:02

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

GOTO EOF

:8095

REM authorization fail 401
curl -v http://localhost:%1/sdata/billingboss/crmErp/-

REM authorization request OK
curl -v http://localhost:%1/sdata/billingboss/crmErp/-

REM get count linked customers
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked?count=0

REM get count all customers
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5?count=0

REM get all customers
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5?select=%select%

REM post customer new links
curl -v -X POST http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked

REM create sync request
curl -v -X POST http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource?trackingId=%2&runName=%5&runStamp=2010-10-14T08:51:02

REM sync request in progress
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM sync feed
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM delete sync request
curl -v -X DELETE http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

GOTO EOF

:9050

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-

REM get count linked invoices
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked?count=0

REM get count all invoices
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?count=0

REM get all invoices
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?select=%select%

REM post 5 invoice new links
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload/></entry>" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload/></entry>" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload/></entry>" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload/></entry>" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload/></entry>" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked

REM create sync request
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload><digest/></payload></entry>" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource?trackingId=%2&runName=%5&runStamp=2010-10-14T08:51:02

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

GOTO EOF


:EOF
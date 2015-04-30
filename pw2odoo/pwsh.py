#!/usr/bin/python

from os import getenv
import sys, getopt
import pymssql
import xmlrpclib
import pw2odoo

action = ''
start = 0
end =110
condition = ''

def main(argv):
  
  global action , start , end , condition , dbname , username , pwd
  try:
      opts, args = getopt.getopt(argv,"ha:s:e:c:p:d:u:",["dbname=","username=","pwd","action=","start=","end=","condition"])
  except getopt.GetoptError:
      print 'pywsh.py -a <action> '
      sys.exit(2)
  for opt, arg in opts:
      if opt == '-h':
         print 'pywsh.py -a <action> -s <start> -c <condition>'
         sys.exit()
      elif opt in ("-a", "--action"):
         action = arg
      elif opt in ("-s", "--start"):
         start = arg
      elif opt in ("-d", "--dbname"):
         dbname = arg
      elif opt in ("-u", "--username"):
         username = arg
      elif opt in ("-p", "--pwd"):
         pwd = arg
      elif opt in ("-c", "--condition"):
         condition = arg


if __name__ == "__main__":
   main(sys.argv[1:])


print action;

if action=='partner_import_all':
  start=int(start)
  for x in range(start, end):
    pos = x * 1000
    print ("posicion %d %s"  % (pos,condition))
    #pw2odoo.pw2odoo('localhost:8069',dbname,username,pwd)
    transaction=pw2odoo.pw_cliente('localhost:8069',dbname,username,pwd)
    transaction.import_all(pos)

if action=='partner_import_from_time':
  transaction=pw2odoo.pw_cliente('localhost:8069',dbname,username,pwd)
  transaction.import_from_time(start)

if action=='proveedores_import_all':
  transaction=pw2odoo.pw_proveedor('localhost:8069',dbname,username,pwd)
  transaction.import_all(0)

if action=='proveedor_import_from_time':
  transaction=pw2odoo.pw_proveedor('localhost:8069',dbname,username,pwd)
  transaction.import_from_time(start)

if action=='invoice_import_all':
  start=int(start)
  transaction=pw2odoo.account_invoice('localhost:8069',dbname,username,pwd)
  for x in range(start, end):
    pos = x * 1000
    print ("posicion %d %s"  % (pos,condition))  
    transaction.import_all(pos)



if action=='res_user_import_all':
  transaction=pw2odoo.pw_users('localhost:8069',dbname,username,pwd)
  transaction.import_all(0)
  
if action=='product_template_import_all':
  start=int(start)
  for x in range(start, end):
    pos = x * 1000
    print ("posicion %d %s"  % (pos,condition))
    #pw2odoo.pw2odoo('localhost:8069',dbname,username,pwd)
    transaction=pw2odoo.pw_articulo('localhost:8069',dbname,username,pwd)
    transaction.import_all(pos)

if action=='product_template_import_from_time':
    transaction=pw2odoo.pw_articulo('localhost:8069',dbname,username,pwd)
    transaction.import_from_time(start)


if action=='crm_claim_stage_import_all':
  pw2odoo.crm_claim_stage_import_all()



if action=='crm_claim_import_all':
  #pw2odoo.claim_demo(478)
  start=int(start)
  for x in range(start, end):
    pos = x * 1000
    print ("posicion %d" % (pos))
    pw2odoo.crm_claim_import_all(pos)


if action=='crm_claim_import_from_time':
  pw2odoo.crm_claim_import_from_time(start)




if action=='category_import_all':
  pw2odoo.category_import_all()


if action=='category_map':
  print (pw2odoo.category_maping())



if action=='product_pricelist_import_all':
    pw2odoo.product_pricelist_import_all()



if action=='up_to_date':
    transaction=pw2odoo.pw_cliente('localhost:8069',dbname,username,pwd)
    start=transaction.ir_get_config_parameter('pw.cliente.last_import_time')
    transaction.import_from_time(start)

    #prv_start=pw2odoo.ir_get_config_parameter('pw.proveedor.last_import_time')
    #pw2odoo.proveedor_import_from_time(prv_start)



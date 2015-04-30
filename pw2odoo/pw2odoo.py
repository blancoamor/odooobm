# -*- encoding: utf-8 -*-

import pymssql
import xmlrpclib 
import datetime
import time
import re
import os.path
import pymssql

import base64
from decimal import *

class pw2odoo(object):

    log_type='print'
    country_states = {}
    vat_responsability = {}
    category_map = {}
    supplier_res_id = {}
    res_users_id = {}
    res_partner_id = {}
    claim_stage_id = {}
    claim_stage_map = {"CANCELADO POR EL CLIENTE":"INVALIDO","DEFENSA DEL CONSUMIDOR":"DEFENSA CCONSUMIDOR","EN OBSERVACION":"CONFIRMADO","FALTA RESPUESTA DEL CLIENTE":""
    ,"INICIADO":"INICIADO","PENDIENTE":"RESOLUCION","PENDIENTE DE CAMBIO":"RESOLUCION","PENDIENTE DE ENTREGA":"RESOLUCION","PENDIENTE DE RESOLUCION":"RESOLUCION","PENDIENTE DE VISITA":"",
    "PENDIENTE RESPUESTA DEL CLIENTE":"RESOLUCION","RECLAMO INVALIDO":"INVALIDO","SOLUCIONADO":"SOLUCIONADO",}
    pw_situacion_iva=['','IVA Responsable Inscripto', 'IVA Responsable No Inscripto', 'Responsable Monotributo','IVA Exento' ,'Consumidor Final']


    product_template_id = {}
    product_product_id = {}


    def __init__(self,url,dbname,username,pwd):

        self.url = url
        self.dbname = dbname
        self.username = username
        self.pwd = pwd

        self.connect_odoo()
        self.connect_pw()

    def connect_odoo(self):
        sock_common = xmlrpclib.ServerProxy ('http://'+ self.url +'/xmlrpc/common')

        self.uid = sock_common.login(self.dbname, self.username, self.pwd)
        self.sock = xmlrpclib.ServerProxy('http://'+ self.url +'/xmlrpc/object')


    def connect_pw(self):
        mssql_server = self.ir_get_config_parameter('pw_connect_url')
        mssql_user = self.ir_get_config_parameter('pw_connect_user')
        mssql_password = self.ir_get_config_parameter('pw_connect_password')

        #conecto a la DB, as_dict=True para obtener clave alfanumerica
        conn = pymssql.connect(mssql_server, mssql_user, mssql_password, "PW_gestion",0,60,"cp1252")
        self.cursor = conn.cursor(as_dict=True)


    def ir_set_config_parameter(self,key,value):
      args = [('key', '=', key),]
      ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.config_parameter', 'search', args)
      
      if ids:
        fields = ['id','value','key'] #fields to read

        data = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.config_parameter', 'read', ids, fields)
        parameter ={'value':str(value), 'key':key  }
        partner_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.config_parameter', 'write',ids , parameter)

      else:
        parameter ={'value':str(value), 
                    'key':key ,
        }
            #partner_id = sock.execute(self.dbname, self.uid, self.pwd, 'res.partner', 'create', partner)

        parameter_id = self.sock.execute(dbname, uid, self.pwd, 'irself..confself.ig_parameter', 'create',parameter)
      
    def res_partner_get_id(self,ClienteKey):
      if hasattr(self.res_partner_id, str(ClienteKey)):
        return self.res_partner_id[ClienteKey]
      else :
        model = 'ir.model.data'
        #args = [('name', '=', 'CK' + str(ClienteKey)),('model', '=', 'res.users'),]
        args = [('name', '=', str(ClienteKey)),('model', '=', 'res.partner'),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
        fields = ['res_id'] #fields to read
        data = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', ids, fields)
        if len(data):
          self.res_partner_id[ClienteKey]=data[0]['res_id']
          return self.res_partner_id[ClienteKey]
        else : 
          return 1

    def user_get_id(self,UsuarioKey):
      if hasattr(self.res_users_id, str(UsuarioKey)):
        return self.res_users_id[UsuarioKey]
      else :
        model = 'ir.model.data'
        args = [('name', '=', 'UK' + str(UsuarioKey)),('model', '=', 'res.users'),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
        fields = ['res_id'] #fields to read
        data = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', ids, fields)
        if len(data):
          self.res_users_id[UsuarioKey]=data[0]['res_id']
          return self.res_users_id[UsuarioKey]
        else : 
          return 1
    def claim_stage_get_id(self,estado):

        if hasattr(self.claim_stage_id, str(estado)):
          return self.claim_stage_id[estado]
        else :
          model = 'ir.model.data'
          #args = [('name', '=', 'CK' + str(ClienteKey)),('model', '=', 'res.users'),]
          args = [('name' , '=' ,self.claim_stage_map[estado]),]
          ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'crm.claim.stage', 'search', args)
          fields = ['id'] #fields to read
          data = self.sock.execute(self.dbname, self.uid, self.pwd, 'crm.claim.stage', 'read', ids, fields)
          if len(data):
            self.claim_stage_id[estado]=data[0]['id']
            return self.claim_stage_id[estado]

    def product_template_get_id(self,ArticuloKey):
        
      if hasattr(self.product_template_id, str(ArticuloKey)):
        return self.product_template_id[ArticuloKey]
      else :
        model = 'ir.model.data'
        args = [('name', '=', 'AK' + str(ArticuloKey)),('model', '=', 'product.template'),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
        fields = ['res_id'] #fields to read
        data = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', ids, fields)
        if len(data):
          self.product_template_id[ArticuloKey]=data[0]['res_id']
          return self.product_template_id[ArticuloKey]
        else : 
          return 1

    def supplier_get_id(self,ProveedorKey):
        
      if hasattr(self.supplier_res_id, str(ProveedorKey)):
        return self.supplier_res_id[ProveedorKey]
      else :
        model = 'ir.model.data'
        args = [('name', '=', 'PK' + str(ProveedorKey)),('model', '=', 'res.partner'),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
        fields = ['res_id'] #fields to read
        data = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', ids, fields)
        if len(data):
          self.supplier_res_id[Proveedorproduct_product_get_idKey]=data[0]['res_id']
          return self.supplier_res_id[ProveedorKey]
        else : 
          return 1

    def product_product_get_id(self,ArticuloKey):
      if hasattr(self.product_product_id, str(ArticuloKey)):
        return self.product_product_id[ArticuloKey]
      else :
        model = 'ir.model.data'
        args = [('name', '=', 'AK' + str(ArticuloKey)),('model', '=', 'product.template'),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
        if ids:
          fields = ['res_id'] #fields to read
          data_tmp = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', ids, fields)
          print data_tmp
          args = [('product_tmpl_id', '=', int(data_tmp[0]['res_id'])),]
          print args
          ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'product.product', 'search', args)
          print ids
          if len(ids):
            self.product_template_id[ArticuloKey]=ids[0]
            return self.product_template_id[ArticuloKey]
          else :
            return 12160

    def category_get_id(self,RubroKey):
      if hasattr(self.category_map, str(RubroKey)):
        return self.category_map[RubroKey]
      else :
        model = 'ir.model.data'
        args = [('name', '=', 'RK' + str(RubroKey)),('model', '=', 'product.category'),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
        if ids:
          fields = ['res_id'] #fields to read
          data_tmp = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', ids, fields)

          if len(ids):
            self.category_map[RubroKey]=data_tmp[0]['res_id']
            return self.category_map[RubroKey]


    def check_vat(self,vat):
        cstr = str(vat)
        salt = str(5432765432)
        n = 0
        sum = 0
        if not vat.isdigit:
            return False
        if (len(vat) != 11):
           return False
        while (n < 10):
            sum = sum + int(salt[n]) * int(cstr[n])
            n = n + 1
        op1 = sum % 11
        op2 = 11 - op1
        code_verifier = op2
        if (op2 == 11 or op2 == 10):
            if (op2 == 11):
                code_verifier = 0
            else:
                code_verifier = 9
        if (code_verifier == int(cstr[10])):
            return True
        else:
            return False

    def ir_get_config_parameter(self,key):
      args = [('key', '=', key),]
      ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.config_parameter', 'search', args)
      
      if ids:
        fields = ['value'] #fields to read

        data = self.sock.execute(self.dbname, self.uid,self.pwd, 'ir.config_parameter', 'read', ids, fields)
        return data[0]['value']
      else:
        return false

    def mapping_res_country_state(self):
        args = [('country_id', '=', 11),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'res.country.state', 'search', args)
        fields = ['name','id'] #fields to read
        res_country_states = self.sock.execute(self.dbname, self.uid, self.pwd, 'res.country.state', 'read',ids, fields)
        for country in res_country_states:
          self.country_states[country['name']]=country['id']
        self.country_states['Rio Negro']=self.country_states[u'R\xedo Negro']
        self.country_states['Neuquen']=self.country_states[ u'Neuqu\xe9n']
        self.country_states['Entre Rios']=self.country_states[u'Entre R\xedos']
        self.country_states['Cordoba']=self.country_states[u'C\xf3rdoba']
        self.country_states['Tucuman']=self.country_states[u'Tucum\xe1n']

    def mapping_vat_responsability(self):
        args = []
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'afip.responsability', 'search', args)
        fields = ['name','id'] #fields to read
        afip_vat_responsability = self.sock.execute(self.dbname, self.uid, self.pwd, 'afip.responsability', 'read',ids, fields)
        for responsability in afip_vat_responsability:
          self.vat_responsability[responsability['name']]=responsability['id']




    def import_all(self,start):
        pass

    def import_from_time(self,start):
        pass

    def mapping(self,row):
        pass

    def after_insert_update(self,row,map_object):
        pass

    def insert_update(self,row):
        ids = None
        model = 'ir.model.data'
        args = [('name', '=', str(self.prefixKey) + str(row[self.pwKey])),('model', '=', self.odooModel),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
        if ids :
            map_object=self.update(ids,row)
            self.log('update',row)

        else:
            map_object=self.insert(row)
            self.log('insert',row)
        self.after_insert_update(row,map_object)


    def insert(self,row):
        odooObject=self.mapping(row)
        try:
          odooObject_id = self.sock.execute(self.dbname, self.uid, self.pwd,self.odooModel, 'create', odooObject)
          external_link = {
            'name' : str(self.prefixKey) + str(row[self.pwKey]),
            'model' : self.odooModel,
            'res_id' : odooObject_id, 
          }
          external_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'create', external_link)
          return {'id': external_link , 'map_object':odooObject}

        except ValueError:
          print (row)
          print (odooObject)

    def update(self,ids,row):
        fields = ['res_id'] #fields to read
        data = self.sock.execute(self.dbname, self.uid, self.pwd,'ir.model.data', 'read', ids, fields)
        odooObject=self.mapping(row)
        odoo_id = self.sock.execute(self.dbname, self.uid, self.pwd, self.odooModel, 'write',data[0]['res_id'], odooObject)
        return {'id': data[0]['res_id'] , 'map_object':odooObject}

    def log(self,action,row):
         if(self.log_type=='print'):
            print action + " " + self.pwKey + ":" + str(row[self.pwKey]) + " -> "  + self.odooModel

class pw_proveedor(pw2odoo):
    prefixKey="PK"
    pwKey="ProveedorKey"
    odooModel='res.partner'

    def import_all(self,start):
        self.mapping_res_country_state()
        self.mapping_vat_responsability()

        self.cursor.execute("SELECT prv.*,p.Nombre as NombreProvincia FROM Proveedor prv "
                     "left join localidad l  on (l.LocalidadKey=prv.LocalidadKey) "
                    "left join provincia p  on (l.ProvinciaKey=p.ProvinciaKey) "
        )
        for row in self.cursor:
        	self.insert_update(row)

    def import_from_time(self,start):
        self.mapping_res_country_state()
        self.mapping_vat_responsability()

        self.cursor.execute("select top 1000 prvl.FechaLog,prvl.TipoLog , prv.* , p.Nombre as NombreProvincia "
                     "From ProveedorLog prvl "
                     "join Proveedor prv on (prvl.ProveedorKey=prv.ProveedorKey) "
                     "left join localidad l  on (l.LocalidadKey=prv.LocalidadKey) "
                     "left join provincia p  on (l.ProvinciaKey=p.ProvinciaKey) "

                     "where FechaLog > '%s' "
                     "order by FechaLog asc " % (start))
        last_time=''

        for row in self.cursor:
            self.insert_update(row)
            last_time=row['FechaLog']

        if(last_time):
            self.ir_set_config_parameter('pw.proveedor.last_import_time',last_time.strftime("%Y-%m-%d %H:%M:%S"))


    def mapping(self,row):
          # CAMPOS disponibles
          # id | name | company_id | comment | ean13 | create_date | color | image | use_parent_address | active | 
          # street | supplier | user_id | zip | title | function | country_id | parent_id | employee | type | email | 
          # vat | website | lang | fax | city | street2 | phone | credit_limit | write_date | date | tz | write_uid |
          # display_name | customer | create_uid | image_medium | mobile | ref | image_small | birthdate | is_company | 
          # state_id | commercial_partner_id | notify_email | message_last_post | opt_out | section_id | signup_type | 
          # signup_expiration | signup_token | calendar_last_notif_ack | last_reconciliation_date | debit_limit | vat_subjected 
          
          relations = {
           'Activo':'active',
           'Email':'email',
           'Telefono':'phone',
           'TelefonoMovil':'mobile',
           'Domicilio':'street',
           'Notas':'comment',
           'CodigoPostal':'zip',
           'Localidad':'city',
          }
          if row['RazonSocial'] is None :
            row['RazonSocial']=row['Apellido'] + ' ' + row['Nombre']
            
          partner = {
             'name': row['RazonSocial'].lstrip().rstrip().title(),
             'lang':'es_AR',
             'supplier':1,
          }

          partner['state_id']=self.country_states['Neuquen']

          #if (row['CUIT'] is not None) and (row['CUIT'].replace('-','').replace(' ',''))  :
          # partner['vat'] ='ar'+row['CUIT'].replace('-','').replace(' ','')

          #if (row['CUIT'] is not None) and (check_vat(row['CUIT'].replace('-','').replace(' ','')))  :
          #  partner['vat'] ='ar'+row['CUIT'].replace('-','').replace(' ','')


          if row['SituacionIVAKey'] == 1 :
            partner['is_company']=1
          else:
            relations['Nombre']='firstname'
            relations['Apellido']='lastname'
            if row['Apellido']:
                del partner['name']

          for key in relations:
             if row[key] is not None:
                partner[relations[key]]=row[key]


          #if partner['email']=="[NO POSEE]":
          #  del  partner['email']
          if row['NombreProvincia'] :
             partner['state_id']=self.country_states[row['NombreProvincia']]

          return partner


class pw_cliente(pw2odoo):
    prefixKey=""
    pwKey="ClienteKey"
    odooModel='res.partner'


    def import_all(self,start):
        self.mapping_vat_responsability()
        self.mapping_res_country_state()
        end=start + 1000
        self.cursor.execute("SELECT * FROM "
                     "( SELECT c.*, p.Nombre as NombreProvincia, ROW_NUMBER() OVER (ORDER BY ClienteKey) AS row "
                     "FROM cliente c "
                     "left join localidad l  on (l.LocalidadKey=c.LocalidadKey) "
                     "left join provincia p  on (l.ProvinciaKey=p.ProvinciaKey) "
                     "where RazonSocial <>'' "
                     ") "
                     "a WHERE row > %d AND row <= %d " 
                     % (start,end))

        for row in self.cursor:    
            self.insert_update(row)

    def import_from_time(self,start):
        self.mapping_res_country_state()
        self.mapping_vat_responsability()

        self.cursor.execute("select top 1000 cl.FechaLog,cl.TipoLog , c.* , p.Nombre as NombreProvincia "
                     "From ClienteLOG cl "
                     "join Cliente c on (cl.ClienteKey=c.ClienteKey) "
                     "left join localidad l  on (l.LocalidadKey=c.LocalidadKey) "
                     "left join provincia p  on (l.ProvinciaKey=p.ProvinciaKey) "

                     "where FechaLog > '%s' "
                     "order by FechaLog asc " % (start))
        last_time=''

        for row in self.cursor:    
            self.insert_update(row)
            last_time=row['FechaLog']

        if(last_time):
            self.ir_set_config_parameter('pw.cliente.last_import_time',last_time.strftime("%Y-%m-%d %H:%M:%S"))

    def mapping(self,row):
        # CAMPOS disponibles
        # id | name | company_id | comment | ean13 | create_date | color | image | use_parent_address | active | 
        # street | supplier | user_id | zip | title | function | country_id | parent_id | employee | type | email | 
        # vat | website | lang | fax | city | street2 | phone | credit_limit | write_date | date | tz | write_uid |
        # display_name | customer | create_uid | image_medium | mobile | ref | image_small | birthdate | is_company | 
        # state_id | commercial_partner_id | notify_email | message_last_post | opt_out | section_id | signup_type | 
        # signup_expiration | signup_token | calendar_last_notif_ack | last_reconciliation_date | debit_limit | vat_subjected 

        mob=re.compile('15[4|5|6](\-)*[0-9][0-9][0-9][0-9][0-9][0-9]')
        email_regepx=re.compile('[^@]+@[^@]+\.[^@]+')
        relations = {
        'Activo':'active',
        'Email':'email',
        'Telefono':'phone',
        'TelefonoMovil':'mobile',
        'Domicilio':'street',
        'Notas':'comment',
        'CodigoPostal':'zip',
        'Localidad':'city',
        }
        if row['RazonSocial'] is None :
            row['RazonSocial']=row['Apellido'] + ' ' + row['Nombre']

            




        partner = {
         'name': row['RazonSocial'].lstrip().rstrip().title(),
         'lang':'es_AR',
         'property_account_receivable': 11, #esto esta cacheado ver que hacemo
         'property_account_payable': 11, #esto esta cacheado ver que hacemo
        }

        partner['state_id']=self.country_states['Neuquen']




        #if (row['CUIT'] is not None) and (row['CUIT'].replace('-','').replace(' ',''))  :
        # partner['vat'] ='ar'+row['CUIT'].replace('-','').replace(' ','')

        if (row['CUIT'] is not None) and (self.check_vat(row['CUIT'].replace('-','').replace(' ','')))  :
          partner['vat'] ='ar'+row['CUIT'].replace('-','').replace(' ','')

        if row['Email'] is not None :
          email=email_regepx.search(row['Email'].encode('utf-8', 'ignore'));
          if(email is not None):      
            row['Email']=str(email.group())
          else :
            row['Email']= None
        
        if row['TelefonoMovil'] is not None :    
          mobile=mob.search(row['TelefonoMovil']);
          if(mobile is not None):      
            row['TelefonoMovil']=str(mobile.group())
        if row['TelefonoMovil'] is None  and row['Telefono'] is not None :
          #154581100
          mobile=mob.search(row['Telefono']);
          if(mobile is not None):      
            row['TelefonoMovil']=str(mobile.group())
  
        if hasattr(self.vat_responsability ,self.pw_situacion_iva[row['SituacionIVAKey']]):
          partner['responsability_id']=self.vat_responsability[self.pw_situacion_iva[row['SituacionIVAKey']]]


        if row['SituacionIVAKey'] == 1:
            partner['is_company']=1
        else:
            relations['Nombre']='firstname'
            relations['Apellido']='lastname'
          if row['Apellido']:
              del partner['name']
          else: 
              row['Apellido'] =row['RazonSocial']

        for key in relations:
         if row[key] is not None:
            partner[relations[key]]=row[key]


        #if partner['email']=="[NO POSEE]":
        #  del  partner['email']
        if row['NombreProvincia'] :
         partner['state_id']=self.country_states[row['NombreProvincia']]


        return partner


class category(pw2odoo):
    prefixKey="RK"
    pwKey="RubroKey"
    odooModel='product.category'

    def import_all(self,pw_parent=0,odoo_parent=1):
      
      self.cursor.execute("SELECT * from Rubro "
                     "WHERE activo =1 and PadreRubroKey = %d  order by Nombre asc " 
                     % (pw_parent))
      for row in self.cursor.fetchall():
        self.insert_update(self,row,odoo_parent)

    def insert_update(self,row,odoo_parent):
        ids = None
        model = 'ir.model.data'
        args = [('name', '=', str(self.prefixKey) + str(row[self.pwKey])),('model', '=', self.odooModel),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
        if ids :
            self.update(ids,row)
        else:
            self.insert(row)
    def insert_category(self,row,odoo_parent=1):

      category = {
         'name': row['Nombre'].lstrip().rstrip().title(),
         'parent_id': odoo_parent,
      }

      category_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'product.category', 'create', category)
      external_link = {
        'name' : "RK" + str(row['RubroKey']),
        'model' : 'product.category',
        'res_id' : category_id, 
      }
      external_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'create', external_link)
      self.category_import_all(row['RubroKey'],category_id)

    def update_category(ids,row,odoo_parent=1):
      fields = ['res_id'] #fields to read
      data = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', ids, fields)
      category = {
         'name': row['Nombre'].lstrip().rstrip().title(),
         'parent_id': odoo_parent,
      }
      category_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'product.category', 'write',data[0]['res_id'], category)

class crm_claim(pw2odoo):
    prefixKey="ERK"
    pwKey="EventoKey"
    odooModel='crm.claim'

    def import_from_time(start):

      cursor.execute("select   e.* , ee.Estado ,e.UsuarioKey as usuario , evest.fecha as fechacambioestado "
                     "from EventoEstado evest "
                     "join evento e  on (e.EventoKey=evest.EventoKey)"
                     "join estadoevento ee on (ee.EstadoKey = evest.EstadoKey) "
                     "join eventotipo et on (et.EventoTipoKey = e.EventoTipoKey) "
                     "where et.tipo=0 "
                     
                     "and  Fecha > '%s' "
                     "order by Fecha asc " % (start))
      last_time=''

    def mapping(row):
      row['partner_id']=self.res_partner_get_id(row['ClienteKey'])
      row['stage_id']=self.claim_stage_get_id(row['Estado'])
      row['user_id']=self.user_get_id(row['UsuarioKey'])
      row['user_state_id']=self.user_get_id(row['usuario'])

      relations = {
       'Activo':'active',
       'FechaIngreso': 'create_date',

       #'FechaGeneracion': 'date',
       'Descripcion': 'description',
      }
      
      crm_claim = {
         'name': row['Titulo'].lstrip().rstrip().title(),
         'partner_id': row['partner_id'],
         'stage_id' :  row['stage_id'] ,
         'create_uid' : row['user_id'] ,
         'create_date' : row['FechaGeneracion'].strftime('%Y/%m/%d %H:%M') ,
         'write_date' : row['fechacambioestado'].strftime('%Y/%m/%d %H:%M') ,
         'date' : row['FechaIngreso'].strftime('%Y/%m/%d ') ,
         'user_id' : row['user_state_id'] ,

      }
      products_id=[]

      if row['ArticuloKey1']:
        product_id=product_product_get_id(row['ArticuloKey1'])
        if product_id :
         products_id.append(product_id)
         #crm_claim['ref']='product.product,'+str(product_id)

      if row['ArticuloKey2'] and row['ArticuloKey1'] != row['ArticuloKey2']:
        product_id=product_product_get_id(row['ArticuloKey2'])
        if product_id :
         products_id.append(product_id)


      if products_id:
        crm_claim['products_id']=[(6,0,products_id)]


      for key in relations:
         if row[key] is not None:
            crm_claim[relations[key]]=row[key]

      crm_claim['origin']='PW Gestion'

      return crm_claim


class pricelist(pw2odoo):
    prefixKey="LPK"
    pwKey="ListaPreciosKey"
    odooModel='product.pricelist'

    def import_all(self,start):
      
      self.cursor.execute("SELECT * FROM listaprecios ")
      for row in self.cursor.fetchall():
        self.insert_update(self,row)

    def mapping(row):
      relations = {
       'Activo':'active',
      }
      product_pricelist = {
        'name': row['Nombre'].lstrip().rstrip().title(),
        'type': 'sale',
        'currency_id' : 20 ,
      }


      for key in relations:
         if row[key] is not None:
            product_pricelist[relations[key]]=row[key]

      return product_pricelist

class pricelist_version(pw2odoo):
    prefixKey="LPKV"
    pwKey="ListaPreciosKey"
    odooModel='product.pricelist.version'

    def import_all(self,start):
      
      self.cursor.execute("SELECT * FROM listaprecios ")
      for row in self.cursor.fetchall():
        self.insert_update(self,row)

    def mapping(row,pricelist_id):
      relations = {
         'Activo':'active',
      }

      product_pricelist = {
        'name': row['Nombre'].lstrip().rstrip().title(),
        'pricelist_id': pricelist_id,
      }


      for key in relations:
         if row[key] is not None:
            product_pricelist[relations[key]]=row[key]

      return product_pricelist



class pw_users(pw2odoo):
    prefixKey="UK"
    pwKey="UsuarioKey"
    odooModel='res.users'

    def import_all(self,start):
      
      self.cursor.execute("SELECT * from Usuario WHERE activo =1 and UsuarioKey<>1  ")
      for row in self.cursor.fetchall():
        self.insert_update(self,row)

    def mapping(row):
      partner = {
         'name': row['Nombre'].lstrip().rstrip().title(),
         'active':row['Activo'],
         'lang':'es_AR',
      }

      partner_id = sock.execute(self.dbname, self.uid, self.pwd, 'res.partner', 'create', partner)

      user = {
         'login': row['Nombre'],
         'password': row['Contrasenia'],
         'partner_id': partner_id,
      }
      return user

    def update(self,ids,row):
      print "not update"

      
      return user




class pw_invoice(pw2odoo):
    prefixKey="OK"
    pwKey="OperacionKey"
    odooModel='res.users'

    def import_all(self,start):
      
      self.cursor.execute("SELECT * from Usuario WHERE activo =1 and UsuarioKey<>1  ")
      for row in self.cursor.fetchall():
        self.insert_update(self,row)

    def mapping(row):
      partner = {
         'name': row['Nombre'].lstrip().rstrip().title(),
         'active':row['Activo'],
         'lang':'es_AR',
      }

      partner_id = sock.execute(self.dbname, self.uid, self.pwd, 'res.partner', 'create', partner)

      user = {
         'login': row['Nombre'],
         'password': row['Contrasenia'],
         'partner_id': partner_id,
      }
      return user

    def update(self,ids,row):
      print "not update"

      
      return user


class pw_articulo(pw2odoo):
    prefixKey="AK"
    pwKey="ArticuloKey"
    odooModel='product.template'

    def import_all(self,start):
      end=start+1000

      self.cursor.execute("SELECT * FROM "
                 "( SELECT a.*,ap.Descripcion as DescripcionProv, CodigoProv, Costo1, p.RazonSocial as NombreProveedor, ROW_NUMBER() OVER (ORDER BY a.ArticuloKey) AS row "
                 "FROM Articulo a "
                 "left join ArticuloProveedor ap on (a.ArticuloKey=ap.ArticuloKey) "
                 "left join proveedor p on (p.ProveedorKey = ap.ProveedorKey) "

                 "where a.Nombre <>'' "
                 ") "
                 "a WHERE row > %d AND row <= %d " 
                 % (start,end))

      for row in self.cursor.fetchall():
        self.insert_update(row)


    def import_from_time(self,start):

      self.cursor.execute("SELECT al.FechaLog, a.*,ap.Descripcion as DescripcionProv, CodigoProv, Costo1, p.RazonSocial as NombreProveedor, ROW_NUMBER() OVER (ORDER BY a.ArticuloKey) AS row "
                     "From ArticuloLog al "
                     "join Articulo a on (a.ArticuloKey=al.ArticuloKey)"
                     "left join ArticuloProveedor ap on (a.ArticuloKey=ap.ArticuloKey) "
                     "left join proveedor p on (p.ProveedorKey = ap.ProveedorKey) "

                     "where a.Nombre <>'' and FechaLog > '%s'"
                     % (start))

      last_time=''
      for row in self.cursor:
        self.insert_update(row)
        last_time=row['FechaLog']

      if(last_time):
        ir_set_config_parameter('pw.articulo.last_import_time',last_time.strftime("%Y-%m-%d %H:%M:%S"))


    def mapping(self,row):


      relations = {
       'Activo':'active',
       'Codigo' : 'default_code',
       #'PrecioVenta':'list_pice',
      }
      

      product_template = {
        'name': row['Nombre'].lstrip().rstrip().title(),
        'mes_type':'fixed',
        'uom_id':1,
        'uom_po_id':1,
        'type':'consu',
        'procure_method':'make_to_stock',
        'cost_method':'standard',

      }
      if(os.path.isfile("./images/" + row['Codigo'] )):
          print "Existe " +  row['Codigo']
          #fileImage = request.files.get("./images/" + row['Codigo'] )
          #image = fileImage.file.read()
          f = open("./images/" + row['Codigo'], "rb")
          image = f.read()
          product_template['image'] = base64.b64encode(image)
          os.rename("./images/" + row['Codigo'] , "./images/proccess_" + row['Codigo'] )

      if row['Costo1'] is not None:
            product_template['standard_price']=float(row['Costo1']);

      product_template['categ_id']=13
      for key in relations:
         if row[key] is not None:
            product_template[relations[key]]=row[key]


      product_template['list_pice']= float(row['PrecioVenta'])


      category=self.category_get_id(row['RubroKey'])
      if category:
        product_template['categ_id']=category

      return product_template
    

    def after_insert_update(self,row,map_object):
        ids = None

        model = 'ir.model.data'
        args = [('name', '=', 'APK' + str(row['ArticuloKey'])),('model', '=', 'product.supplierinfo'),]
        ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
        if ids :
          self.product_supplierinfo_update(ids,row,map_object['id'])
        else:
          self.product_supplierinfo_insert(row,map_object['id'])

             
    def product_supplierinfo_mapping(self,row,product_res_id):
      if row['DescripcionProv'] is None:
        desc = row['Nombre'].lstrip().rstrip().title()
      else :
        desc = row['DescripcionProv'].lstrip().rstrip().title()

      if row['CodigoProv'] is None:
        CodigoProv = '000'
      else :
        CodigoProv = row['CodigoProv'].lstrip().rstrip().title()

      supplier_id = self.supplier_get_id(row['ProveedorKey'])
      product_supplierinfo = {
        'product_name': desc,
        'product_code': CodigoProv,
        'product_tmpl_id': product_res_id ,
        'name' : str(supplier_id),

      }

      return product_supplierinfo

    def product_supplierinfo_insert(self,row,product_res_id):
      product_supplierinfo = self.product_supplierinfo_mapping(row,product_res_id)  
      product_supplierinfo_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'product.supplierinfo', 'create', product_supplierinfo)
      
      external_link = {
        'name' : 'APK' + str(row['ArticuloKey']),
        'model' : 'product.supplierinfo',
        'res_id' : product_supplierinfo_id, 
      }
      external_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'create', external_link)
      #pricelist_partnerinfo_insert_update(row,product_supplierinfo_id)

    def product_supplierinfo_update(self,ids,row,product_res_id):
      fields = ['res_id'] #fields to read
      data = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', ids, fields)
      product_supplierinfo = self.product_supplierinfo_mapping(row,product_res_id)  
      product_supplierinfo_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'product.supplierinfo', 'write',data[0]['res_id'], product_supplierinfo)
      self.pricelist_partnerinfo_insert_update(row,data[0]['res_id'])

    def pricelist_partnerinfo_insert_update(self,row,suppinfo_id):
      ids = None
      model = 'ir.model.data'
      args = [('name', '=', 'PPI' + str(row['ArticuloKey'])),('model', '=', 'pricelist.partnerinfo'),]
      ids = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'search', args)
      if ids :
        self.pricelist_partnerinfo_update(ids,row,suppinfo_id)
      else:
        self.pricelist_partnerinfo_insert(row,suppinfo_id)


    def pricelist_partnerinfo_insert(self,row,suppinfo_id):
      pricelist_partnerinfo = self.pricelist_partnerinfo_mapping(row,suppinfo_id)  
      pricelist_partnerinfo_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'pricelist.partnerinfo', 'create', pricelist_partnerinfo)
      external_link = {
        'name' : 'PPI' + str(row['ArticuloKey']),
        'model' : 'pricelist.partnerinfo',
        'res_id' : pricelist_partnerinfo_id, 
      }
      external_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'create', external_link)



    def pricelist_partnerinfo_update(self,ids,row,suppinfo_id):
      fields = ['res_id'] #fields to read
      data = self.sock.execute(self.dbname, self.uid, self.pwd, 'ir.model.data', 'read', ids, fields)
      pricelist_partnerinfo = self.pricelist_partnerinfo_mapping(row,suppinfo_id)  
      pricelist_partnerinfo_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'pricelist.partnerinfo', 'write',data[0]['res_id'], pricelist_partnerinfo)

    def pricelist_partnerinfo_mapping(self,row,suppinfo_id):
      pricelist_partnerinfo = {
        'suppinfo_id': suppinfo_id,
        'min_quantity': 1,

      }
      if row['Costo1']:
        pricelist_partnerinfo['price']= float(row['Costo1'])
      else:
        pricelist_partnerinfo['price']= 0.0

      return pricelist_partnerinfo


class account_invoice(pw2odoo):
    prefixKey="FK"
    pwKey="OperacionKey"
    odooModel='account.invoice'

    def import_all(self,start):
      end=start+100

      self.cursor.execute("SELECT * FROM "
                 "(SELECT  ov.* , ROW_NUMBER() OVER (ORDER BY ov.OperacionKey) AS row "
                 "from OperacionVenta ov "
                 ") "
                 "a WHERE row > %d AND row <= %d " 
                 % (start,end))

      for row in self.cursor.fetchall():
        self.insert_update(row)



    def mapping(self,row):

      '''
       id | comment | origin | check_total | partner_bank_id | payment_term | number | write_uid | create_uid | user_id | supplier_invoice_number | 
       message_last_post | company_id | amount_tax | type | sent | internal_number | account_id | date_invoice | period_id | amount_total | name | 
       commercial_partner_id | date_due | create_date | reference | currency_id | partner_id | fiscal_position | amount_untaxed | reference_type | 
       journal_id | state | reconciled | residual | move_name | write_date | move_id | section_id | afip_service_start | afip_service_end | 
       afip_document_class_id | afip_document_number | journal_document_class_id | responsability_id 
      '''

      partner_id=self.res_partner_get_id(row['ClienteKey'])
      if partner_id==1:
        partner_id=79495 #to-do ver consumidor final

      #user_id = user_get_id(row['VendedorKey']) #VendedorKey


      relations = {
       'Numero':'number',
      }
      #CondicionPagoKey
      #Clase

      account_invoice = {
        #'create_date' : row['FechaFactura'].strftime('%Y/%m/%d %H:%M') ,
        #'write_date' : row['FechaFactura'].strftime('%Y/%m/%d %H:%M') ,

        'date_invoice':row['FechaFactura'].strftime('%Y/%m/%d %H:%M'), 
        'partner_id':partner_id,
        'currency_id' : 20,
        'number' : row['Numero'].lstrip().rstrip(),
        'account_id' : 11 ,
        'amount_total' : float(row['ImporteTotal']),

        'amount_untaxed' : float(row['SumaItemsNG']),
        'amount_tax' : float(row['MontoIVA']) ,

      }
      products=self.operacion_venta_articulos(row['OperacionKey'],account_invoice)
      account_invoice['invoice_line']=[(6,0,products)]
      
      '''for key in relations:
               if row[key] is not None:
                  account_invoice[relations[key]]=row[key]
      '''
      return account_invoice
      
    def operacion_venta_articulos(self,OperacionKey,order):
      '''
       id | product_uos_qty |        create_date         | product_uom | sequence | order_id | price_unit | product_uom_qty | write_uid 
       | discount |         write_date         | product_uos | salesman_id | invoiced | create_uid | product_id | company_id |name| delay
        |   state   | order_partner_id | th_weight | address_allotment_id 

      '''
      lines=[]
      self.cursor.execute("select * from VentaItem where OperacionKey= %d" 
                 % (OperacionKey))

      for row in self.cursor.fetchall():
        #product_id=self.product_product_get_id(row['ArticuloKey'])
        product_id=self.product_template_get_id(row['ArticuloKey'])
        line={'uos_id':1,'product_uom_qty': float(row['Cantidad']) ,'price_unit':float(row['PrecioUnitarioFinal']),
          'price_subtotal':float(row['PrecioTotalFinal']), 
          'name':row['Descripcion'], 'product_id':product_id,'discount':float(row['PorcentajeDescuento']),'create_date':order['date_invoice'],
          'order_partner_id' :  order['partner_id'],'account_id':87}

        line_id = self.sock.execute(self.dbname, self.uid, self.pwd, 'account.invoice.line', 'create', line)
        lines.append(line_id)

        
        '''lines.append({'uos_id':1,'product_uom_qty': float(row['Cantidad']) ,'price_unit':float(row['PrecioUnitarioFinal']),
          'price_subtotal':float(row['PrecioTotalFinal']), 
          'name':row['Descripcion'], 'product_id':product_id,'discount':float(row['PorcentajeDescuento']),'create_date':order['date_invoice'],
          'order_partner_id' :  order['partner_id'],'account_id':87})
        #print lines
        #self.insert_update(row)'''
      return lines
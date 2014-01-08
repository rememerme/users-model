from cassa import CassaModel
from django.db import models
import pycassa
from django.conf import settings
import uuid
from rest_framework import serializers
import hashlib

# User model faked to use Cassandra
POOL = pycassa.ConnectionPool('users', server_list=settings.CASSANDRA_NODES)

class User(CassaModel):
    table = pycassa.ColumnFamily(POOL, 'user')
    
    user_id = models.TextField(primary_key=True)
    premium = models.BooleanField()
    email = models.TextField()
    username = models.TextField()
    salt = models.TextField()
    password = models.TextField()
    facebook = models.BooleanField()
    active = models.BooleanField()
    
    '''
        Creates a User object from a map object with the properties.
    '''
    @staticmethod
    def fromMap(mapRep):
        return User(**mapRep)
    
    '''
        Creates a User object from the tuple return from Cassandra.
    '''
    @staticmethod
    def fromCassa(cassRep):
        mapRep = {key : val for key, val in cassRep[1].iteritems()}
        mapRep['user_id'] = str(cassRep[0])
        
        return User.fromMap(mapRep)
    
    '''
        Method for getting single users from cassandra given the email, username or user_id.
    '''
    @staticmethod
    def get(user_id=None, username=None, email=None):
        if user_id:
            return User.getByID(user_id)
        
        if username:
            return User.getByUsername(username)
        
        if email:
            return User.getByEmail(email)
        
        return None
    
    '''
        Gets the user given an ID.
        
        @param user_id: The uuid of the user.
    '''
    @staticmethod
    def getByID(user_id):
        if not isinstance(user_id, uuid.UUID):
            user_id = uuid.UUID(user_id)
        return User.fromCassa((str(user_id), User.table.get(user_id)))
    
    '''
        Gets the user given a username.
        
        @param username: The username of the user.
    '''
    @staticmethod
    def getByUsername(username):
        expr = pycassa.create_index_expression('username', username)
        clause = pycassa.create_index_clause([expr], count=1)
        ans = list(User.table.get_indexed_slices(clause))
        
        if len(ans) == 0:
            return None
        
        return User.fromCassa(ans[0])
    
    '''
        Gets the user by the email.
        
        @param email: The email of the user.
    '''
    @staticmethod
    def getByEmail(email):
        expr = pycassa.create_index_expression('email', email)
        clause = pycassa.create_index_clause([expr], count=1)
        ans = list(User.table.get_indexed_slices(clause))
        
        if len(ans) == 0:
            return None
        
        return User.fromCassa(ans[0])
    
    '''
        Gets all of the users and uses an offset and limit if
        supplied.
        
        @param offset: Optional argument. Used to offset the query by so
            many entries.
        @param limit: Optional argument. Used to limit the number of entries
            returned by the query.
    '''
    @staticmethod
    def all(limit=settings.REST_FRAMEWORK['PAGINATE_BY'], page=None):
        if not page:
            return [User.fromCassa(cassRep) for cassRep in User.table.get_range(row_count=limit)]
        else:
            if not isinstance(page, uuid.UUID):
                page = uuid.UUID(page)
            gen = User.table.get_range(start=page, row_count=limit + 1)
            gen.next()
            return [User.fromCassa(cassRep) for cassRep in gen]
    
    '''
        Hashes a password with the given salt. If no salt is provided, the salt that will be
        used is an empty string.
    '''
    @staticmethod
    def hash_password(password, salt=''):
        password = password.encode('utf8') if isinstance(password, unicode) else password
        salt = salt.encode('utf8') if isinstance(salt, unicode) else salt
        
        return unicode(hashlib.sha256(salt + password).hexdigest())
    
    '''
        Saves a set of users given by the cassandra in/output, which is
        a dictionary of values.
        
        @param users: The set of users to save to the user store.  
    '''
    def save(self):
        user_id = uuid.uuid1() if not self.user_id else uuid.UUID(self.user_id)
        User.table.insert(user_id, CassaUserSerializer(self).data)
        self.user_id = user_id
        
        
        
'''
    The User serializer used to create a python dictionary for submitting to the
    Cassandra database with the correct options.
'''
class CassaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'salt', 'password', 'active', 'facebook', 'premium')

    
    
    

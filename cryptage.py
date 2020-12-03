import binascii
import os
import arithmetic
import rsa


class RSAEncryption:
    
    def __init__(self,use_to_encrypt=True):
        if use_to_encrypt == True:
            self.clepublic = int()
        else:
            self.cleprivee = int()
    
    def set_private_key(self,cleprivee):
        self.cleprivee = cleprivee
    
    def set_public_key(self,clepublic):
        self.clepublic = clepublic

    @classmethod
    def generate_key(cls,nbit=8):
        """
            Return p,q,e,d,phi,n
        """
        p = arithmetic.obtenir_un_nombre_premier(nbit)
        q = arithmetic.obtenir_un_nombre_premier(nbit)
        n = p*q
        phi = (p-1)*(q-1)
        e = arithmetic.get_exponent(phi)

        _, d, _ = arithmetic.algorithme_deuclide(e, phi)
        return (p, q, e, abs(d)%phi, phi,  n)

    @classmethod
    def clevalide(cls,e,d,n,nbit):
        _r = 2**nbit
        _c = pow(_r, e, n)
        _d = pow(_c, d, n)
        return _r == _d

    @classmethod
    def cle(cls,nbit=8):
        """
            cleprive , clepublic, n
        """
        _, _, e, d ,_, n = cls.generate_key(nbit)
        while not cls.clevalide(e,d,n,nbit):
            _, _, e, d, _, n = cls.generate_key(nbit)
        return (hex(d), hex(e), hex(n))

    @classmethod
    def _key(cls,nbit):
        pub, priv = rsa.key.newkeys(nbit)
        return hex(priv.d),hex(pub.e),hex(pub.n)

    def crypter(self,message):
        e, n = int(self.clepublic[0], base=16), int(self.clepublic[1], base=16)
        __message = str(message)
        __intmessage = arithmetic.convert_str_int(__message)
        if __intmessage >= n | __intmessage < 0:
            raise ValueError('0 <= m < n')
        crypted = pow(__intmessage, e, n)
        return hex(crypted)
    
    def crypter_bin(self, message):
        e, n = int(self.clepublic[0], base=16), int(self.clepublic[1], base=16)
        __intmessage = rsa.transform.bytes2int(message)
        if __intmessage >= n | __intmessage < 0:
            raise ValueError('0 <= m < n')
        crypted = pow(__intmessage, e, n)
        return hex(crypted)

    def tuple_crypter(self,message):
        return ( self.crypter(message[0]), self.crypter(message[1]) )
    
    def decrypter(self,crypto):
        d, n = int(self.cleprivee[0], base=16), int(self.cleprivee[1], base=16)
        __crypto = int(crypto,base=16)
        decrypted = pow(__crypto,d,n)
        return arithmetic.convert_int_str(decrypted)

    def decrypter_bin(self, crypto):
        d, n = int(self.cleprivee[0], base=16), int(self.cleprivee[1], base=16)
        __crypto = int(crypto, base=16)
        decrypted = pow(__crypto, d, n)
        return rsa.transform.int2bytes(decrypted)
        
             
    def tuple_decrypter(self,message):
        return ( self.decrypter(message[0]), self.decrypter(message[1]) )


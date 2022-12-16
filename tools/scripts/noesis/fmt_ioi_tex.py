from inc_noesis import *


def registerNoesisTypes():
    handle = noesis.register("IO Iterective textures", ".tex")

    noesis.setHandlerTypeCheck(handle, ioCheckType)
    noesis.setHandlerLoadRGBA(handle, ioLoadRGBA)
    
    return 1
  
  
class ioTexure:  
    def __init__(self):
        self.pos = 0
        self.sectionSize = 0
        self.textureDataSize = 0
        self.width = 0
        self.height = 0
        self.name = ""
        self.data = None
        self.id = None

    def readHeader(self, filereader):   
       
        self.sectionSize = filereader.readUInt()
        self.id = filereader.readBytes(4).decode("ascii").rstrip('\0')
        
        filereader.seek(8, NOESEEK_REL) 
        
        self.width = filereader.readUShort() 
        self.height = filereader.readUShort()         
        
        filereader.seek(16, NOESEEK_REL)      
 
        self.name = filereader.readString()
    
    def readData(self, reader):
        if self.id == "NLAP":
            size1 = reader.readUInt() 
            indexes = reader.readBytes(size1)
            size2 = reader.readUInt() 
            palleteRGBA = reader.readBytes(size2*4)            
            # apply pallete            
            self.data = bytearray(self.height * self.width * 4)
            for i in range(size1):
                self.data[i*4 + 0] = palleteRGBA[indexes[i]*4 + 0] 
                self.data[i*4 + 1] = palleteRGBA[indexes[i]*4 + 1]
                self.data[i*4 + 2] = palleteRGBA[indexes[i]*4 + 2]
                self.data[i*4 + 3] = palleteRGBA[indexes[i]*4 + 3]
        else:
            self.textureDataSize = reader.readUInt()    
            self.data = reader.readBytes(self.textureDataSize)                                         

    def read(self, reader):
        self.pos = reader.tell()
        self.readHeader(reader)        
        self.readData(reader)
        reader.seek(self.pos + self.sectionSize, NOESEEK_ABS)  #skip       
        
        
class ioTEXFile:
    def __init__(self, reader):
        self.filereader = reader
        self.size1 = 0
        self.size2 = 0
        self.textures = []
 
    def parseHeader(self): 
        self.filereader.seek(0, NOESEEK_ABS)    
        self.size1 = self.filereader.readUInt() 
        self.size2 = self.filereader.readUInt() 
        self.filereader.readUInt() 
        self.filereader.readUInt() 
        
        return 0                           
 
    def readTextures(self):        
        while self.size1 > self.filereader.tell():
            tex = ioTexure()
            tex.read(self.filereader)        
            
            self.textures.append(tex)             

    def read(self): 
        self.parseHeader()
        self.readTextures()
        
    
def ioCheckType(data):
    file = ioTEXFile(NoeBitStream(data))
    if file.parseHeader() != 0:
        return 0
        
    return 1  


def ioLoadRGBA(data, texList):

    file = ioTEXFile(NoeBitStream(data))
    if file.parseHeader() != 0:
        return 0 
        
    file.read()    
    # noesis.logPopup()
    
    ids = {"ABGR": noesis.NOESISTEX_RGBA32, "1TXD": noesis.NOESISTEX_DXT1, \
        "3TXD": noesis.NOESISTEX_DXT3, "NLAP": noesis.NOESISTEX_RGBA32}
    
    for tex in file.textures:
        type = ids.get(tex.id, None)
        
        if type:        
            texList.append(NoeTexture(tex.name, tex.height, tex.width, tex.data, \
            type))
        else:          
            print(tex.id)
            
    return 1         
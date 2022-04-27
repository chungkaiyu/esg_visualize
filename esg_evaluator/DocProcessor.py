import fitz
import docx
import re

class DocProcessor:
    """
    Load text from pdf or docx document.
    It will 
    """
    def __init__(self):
        self.text =  ''
        self.sign_string = ''' -.,()[]{}:；'"!?%'''

    def set_sign(self,sign_string):
        """
        Set the punctuation marks to be kept in the text, otherwise it will be deleted
        """
        self.sign_string = sign_string

    def is_number(self, uchar):
        if uchar >= u'\u0030' and uchar<=u'\u0039':
            return True
        else:
            return False
      
    def is_alphabet(self, uchar):
        if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
            return True
        else:
            return False
    def is_sign(self,uchar):
        if uchar in set(self.sign_string):
            return True
        else:
            return False
    def is_char(self, uchar):
        if not (self.is_alphabet(uchar) or self.is_number(uchar) or self.is_sign(uchar)):
            return True
        else:
            return False

    def read_pdf_text(self,pdf,page_no=-1):
        page_content=[]
        text=''

        for page in pdf:
            # use get_text('blocks') instead of get_text('text')
            # each blocks entry is [x0, y0, x1, y1, word, block_id, line_id]
            blocks = page.get_text('blocks')
            blocks = sorted(blocks, key = lambda b: (b[0], b[1]))

            for block_word in blocks:
                if block_word[4].startswith( '<image:'):
                    continue
                elif len( block_word[4].replace('\n','') ) < 10:
                    continue
                page_content.append(block_word[4])
    
        for page_num in range(len(page_content)):
            for j in page_content[page_num]:
                if j == '\n' or self.is_char(j):
                    page_content[page_num] = page_content[page_num].replace(j, ' ')
        
        return '\n'.join(page_content)

    # docx text reader
    def raed_doc_text(filename):
        doc = docx.Document(filename)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)

    # filename extension
    def get_file_text(self, filename):
        f_extension = filename.split('.')[-1]
        if f_extension in ["docx","doc"]:
            text = self.raed_doc_text(filename)
        elif f_extension == "pdf":
            pdf = fitz.open(filename)
            text = self.read_pdf_text(pdf=pdf)
        else:
            print("Unknow Filename Extension")
        print("Read Successfully")
        return text

    ### extension

    # get text with page number, e.g. { 1:"page_1_content", ... }
    def read_pdf_text_with_pageNo(self, pdf, page_no=-1 ):
        page_content=[]
        no = 0
        for i in pdf:
            page_content.append(" ")

        for page in pdf:
            # use get_text('blocks') instead of get_text('text')
            # each blocks entry is [x0, y0, x1, y1, word, block_id, line_id]
            blocks = page.get_text('blocks')
            blocks = sorted(blocks, key = lambda b: (b[0], b[1]))
            #print('page_num:'+str(no)+' blocks:'+str(len(blocks)))
            for block_word in blocks:
                if block_word[4].startswith( '<image:'):
                    continue
                elif len( block_word[4].replace('\n','') ) < 10:
                    continue

                page_content[no] += (block_word[4]+" | ")
            no+=1

        res = {}
        for page_num in range(len(page_content)):
            page_content[page_num] = page_content[page_num].replace("\n", " ")
            res[int(page_num)+1] = page_content[page_num].split()
        print(res[1])
        return res
            

    # get text with page, e.g. { 1:"page_1_content", ... }
    def get_file_text_with_pageNo( self, filename ):
        f_extension = filename.split('.')[-1]
        if f_extension in ["docx","doc"]:
            text = self.raed_doc_text(filename)
        elif f_extension in ["pdf","PDF"]:
            pdf = fitz.open(filename)
            text = self.read_pdf_text_with_pageNo(pdf=pdf)
        else:
            print("Unknow Filename Extension")
        print("Read Successfully")
        return text
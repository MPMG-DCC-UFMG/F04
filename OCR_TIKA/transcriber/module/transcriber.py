import requests
import subprocess
import json 

class TikaTranscriber():
  def __init__(self, bearer_token):
    #Componentes da chamada da API.
    self.command_line_call = f"curl -k -X POST 'https://servicosgsi.mpmg.mp.br/tika/1.24/img_to_txt' -H 'accept: application/json' -H 'Content-Type: multipart/form-data' -H 'Authorization: Bearer {bearer_token}' -F arquivo=@"
    
    ###To use cURL. Not working, for some reason.
    self.header = {
    'accept': 'application/json',
    'Content-Type': 'multipart/form-data',
    'Authorization': f'Bearer {bearer_token}',
    }

    self.link = 'https://servicosgsi.mpmg.mp.br/tika/1.24/img_to_txt'
  
  def transcribe_single_image(self, path):
    final_command = self.command_line_call+path
    response = subprocess.getstatusoutput(final_command)
    jason = response[1].split('\n')[-1]
    jason = json.loads(jason)
    new_dict = {}
    final_text = jason['texto']
    file_name = path.split('/')
    image_name = file_name[-1]
    new_dict[image_name] = final_text
    print(new_dict)
    return new_dict
  

      
  def transcribe_single_image_curl(self, path):
    #not working? Apparently Tecnsys' server doesn't support correctly curl.
    self.file['arquivo'] = (f'{path}', open(f'{path}', 'rb'))
    response = requests.post(self.link, 
                            headers= self.headers, 
                            files=self.file, verify=False)
    
    final_text = response.json()['texto']
     
    return final_text  
  


        
    

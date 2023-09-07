from flask import Flask, jsonify
import main as hltv
import pprint 

app = Flask(__name__)
path = "./data/data.json"

@app.route('/update_brteams_data')
def update_data():
    
    data = hltv.get_brteams_info(['furia', 'imperial', 'pain', 'fluxo', 'oddik', 'oplano', 'mibr'])
   
    conteudo = ""

    with open(path, 'w') as arquivo:
        arquivo.write(str(data))

    with open(path, 'r') as arquivo:
        conteudo = arquivo.read()    
    
    conteudo_corrigido = conteudo.replace("'", '"')   

    with open(path, 'w') as arquivo:
        arquivo.write(conteudo_corrigido)
        print("data.json -> Atualizado")
    
    return "Dados Atualizados"

@app.route('/get_data')
def get_data():
    with open(path, 'r') as arquivo:
        dados = arquivo.read()

    return dados

if __name__ == '__main__':
    app.run(debug=True)
   
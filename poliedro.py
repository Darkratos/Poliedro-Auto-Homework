# Necessary libraries
import requests
import json
import time
import re

# Your login information for Poliedro ( place it inside the quotes )
login = {
    'Usuario': '',
    'Password': ''
}

def main( ):
    # Infinite loop, so it's always checking for new homework
    while( True ):
        # Start an session, so the cookies can be transfered from one request to another
        s = requests.Session( )
        
        # Make a POST request on the login page with your login information
        s.post( 'https://portal.p4ed.com/', data = login )
        
        # Make a GET request to grab the login token
        resp = s.get( 'https://portal.p4ed.com/Login/AutenticacaoPortalEdrosAlunos/0' )
        
        # Search for the login token in the HTML response using Regular Expressions
        login_token = re.search( r"'https:\/\/student\.p4ed\.com\/login\/loginbytoken\/(.+)?'", resp.text ).group( )
        login_token = login_token[ 1 : -1 ]

        # Make a GET request to grab the authorization cookie
        s.get( login_token )

        # Access the actual data for the student
        resp = s.get( 'https://student.p4ed.com/tarefas/dados' )

        # Load the data in a JSON format
        resp_json = json.loads( resp.text )
        
        # If the process fails, display the message
        if ( resp_json[ 'Sucesso' ] == False ):
            print( "[!] Falha ao logar..." )
            break

        # Get the amount of homework ( needed for the loop )
        tarefas_len = len( resp_json[ 'Dados' ][ 'DadosPagina' ][ 'Tarefas' ] )

        for i in range( tarefas_len ):
            # Checks if you haven't concluded the homework
            if resp_json[ 'Dados' ][ 'DadosPagina' ][ 'Tarefas' ][ i ][ 'DataRealizacao' ] == None:
                # Checks if it has a due date
                if resp_json[ 'Dados' ][ 'DadosPagina' ][ 'Tarefas' ][ i ][ 'DataEntrega' ] != None:
                    # Grabs the information about the homework ( not really needed in this version )
                    prof = resp_json[ 'Dados' ][ 'DadosPagina' ][ 'Tarefas' ][ i ][ 'Apelido' ]
                    cont = resp_json[ 'Dados' ][ 'DadosPagina' ][ 'Tarefas' ][ i ][ 'Descricao' ]
                    date = resp_json[ 'Dados' ][ 'DadosPagina' ][ 'Tarefas' ][ i ][ 'DataEntregaUniversal' ].split( 'T' )[ 0 ]
                    
                    hw_id = resp_json[ 'Dados' ][ 'DadosPagina' ][ 'Tarefas' ][ i ][ 'Id' ]
                    
                    # Waits for a second before continuing ( avoids being blocked from Poliedro's system )
                    time.sleep( 1 )
                    
                    # Does a POST request to set the current homework as completed
                    s.post( 'https://student.p4ed.com/tarefas/salvar', data = { "concluidas": hw_id } )
                    
                    # Prints the information about the current homework to the screen
                    print( "[+] Tarefa encontrada: Prof. " + prof + " / Entrega: " + date )
        
        # Waits for another 30 seconds and executes everything again
        time.sleep( 30 )

# Main Call
if __name__ == '__main__':
    main( )

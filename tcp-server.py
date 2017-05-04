# ---------
# python 3.6.0 interpreter
# File: tcp-ttt-server.py
# Description: a web server that handles GET and POST requests from web client
#              using TCP/IP sockets
#              an application server that allows web client to play a game of cross
#              and naughts against this server.

from socket import *
import mimetypes
import os
import random


# -----------------------
# APPLICATION SERVER [Game]
# -----------------------

#global variable(debugging purposes):
#board = ['',' ',' ',' ',' ',' ',' ',' ',' ',' ']

# the winning conditions
def win_conditions(board, move):
    if (board[1]  == move and board[2] == move and board[3] == move) or \
        (board[4] == move and board[5] == move and board[6] == move) or \
        (board[7] == move and board[8] == move and board[9] == move) or \
        (board[1] == move and board[4] == move and board[7] == move) or \
        (board[2] == move and board[5] == move and board[8] == move) or \
        (board[3] == move and board[6] == move and board[9] == move) or \
        (board[1] == move and board[5] == move and board[9] == move) or \
        (board[3] == move and board[5] == move and board[7] == move):
        return True
    else:
        return False

def is_board_full(board):
    if " " in board:
        return False
    else:
        return True

# generate random move that isnt already in game board
def get_random_move(board,move):
    while True:
        compmove = random.randint(1,9)
        if board[compmove] == ' ':
            return compmove
            break

# server game results
def update_game_results(draw, playerwin, compwin, generate_page):
    generate_page = generate_page.decode()
    placeholder = 'Game: Ready'
    if draw:
        results = 'its a draw!'
        generate_page = generate_page.replace(placeholder, results, 1)

    if playerwin:
        results = 'Congratulations! You Win!'
        generate_page = generate_page.replace(placeholder, results, 1)

    if compwin:
        results = 'You Lose. Better luck next time'
        generate_page = generate_page.replace(placeholder, results, 1)
    generate_page = generate_page.encode()

    return generate_page

# generate modified html response page
def updategamepage(board, choice, ren_page):
        strchoice = str(choice)
        strchoice = '-' + strchoice + '-'
        temppage = ren_page.decode()
        generate_page = temppage.replace(strchoice, board[choice], 1)
        generate_page = generate_page.encode()

        return generate_page

def playgame(board, clientmove, ren_page):
    choice = clientmove
    # Check to see if player move is empty
    if board[choice] == ' ':
        board[choice] = 'X'

    generate_page = updategamepage(board, choice, ren_page)

    # Check if player won
    if win_conditions(board, 'X'):
        playerwin = True
        draw = False
        compwin = False

        generate_page = updategamepage(board, choice, generate_page)
        return generate_page, draw, playerwin, compwin

    # Check for a draw
    if is_board_full(board):
        draw = True
        playerwin = False
        compwin = False
        generate_page = updategamepage(board, choice, generate_page)
        return generate_page, draw, playerwin, compwin

    # Get Computer Move
    choice = get_random_move(board, 'O')
    # Check to see if space is empty first
    if board[choice] == ' ':
        board[choice] = 'O'

    generate_page = updategamepage(board, choice, generate_page)

    # Check comp win
    if win_conditions(board, 'O'):
        compwin = True
        draw = False
        playerwin = False
        generate_page = updategamepage(board, choice, generate_page)
        return generate_page, draw, playerwin, compwin

    #Check for a draw
    if is_board_full(board):
        draw = True
        compwin = False
        playerwin = False
        generate_page = updategamepage(board, choice, generate_page)
        return generate_page, draw, playerwin, compwin

    draw = False
    compwin = False
    playerwin = False

    return generate_page, draw, playerwin, compwin

# return true only if move is between 1 to 9, which hasnt already
# been played by player/computer
def is_move_valid(testmove):
    try:
        testmove = int(testmove)
        if (isinstance(testmove, int)):
            if (testmove > 0) and (testmove < 10):
                return True
        else:
            return False
    except:
        return False

# ----------------
# WEB SERVER CODE
# ----------------

# initializeServer
def InitializeServer():
    try:
        serverPort = 10000
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', serverPort))
        serverSocket.listen(5)
        print('--- Waiting for player on port...', serverPort)
    except BaseException as err:
        print('Server failure. \n' + str(err))

    return (serverSocket, serverPort)

# handle GET request
def request_handler(req):
    try:
        req_line, escapechr, req = req.partition(b'\r\n')
        method, route, version = req_line.split(b' ')
        return (method, route, version)
    except:
        method = " "
        route = " "
        version = " "
        return (method, route, version)

# generate response
def response_handler(version, code, phrase, content_type, game_page):
    status_line = version + b' ' + ' '.join([code, phrase]).encode('utf-8')
    connection_status = b'Connection:Keep Alive'
    content_length_line = ('Content-Length: ' + str(len(game_page))).encode()
    content_type_line = ('Content-Type: ' + content_type).encode()
    res_body = game_page

    return b'\r\n'.join([status_line, connection_status, content_length_line, content_type_line + b'\r\n', res_body])

# open directory file and return server directory
def openfile():
    serverdirectory = os.path.join(os.path.dirname(__file__))
    path = os.path.join(os.path.dirname(__file__), 'game.html')
    errorpath = os.path.join(os.path.dirname(__file__), 'error.html')
    game_page = open(path, 'rb').read()
    error_page = open(errorpath, 'rb').read()
    return (game_page, path, serverdirectory, error_page)

# check to see if requested file is in the server directory
def fileAvailable(serverdirectory, route):
    #str(bytes_string, 'utf-8')
    #print(type(route))
    #strroute = str(route, 'ASCII')
    #print(type(strroute))
    #strroute = route.decode('ASCII')
    strroute = parseRouteBytes(route)
    print(strroute)
    reqRoute = serverdirectory + strroute
    #reqRoute = reqRoute.decode()
    print(reqRoute)
    if (os.path.isfile(reqRoute)) or strroute == '/':
        return True
    else:
        return False

# parse RouteBytes to str route
def parseRouteBytes(route):

    strroute = str(route) #has b'/route'
    strroute = strroute[2:]#has /route'
    strroute = strroute[:-1]#has /route

    return strroute

# build response message header line
def generateResponseMessage(serverdirectory, method, route, path):
    strroute = parseRouteBytes(route)
    if (fileAvailable(serverdirectory, route)):
        code = '200'
        phrase = 'OK'
        content_type = mimetypes.guess_type(path)[0]
        print('')
        print('-- File Found:' + strroute + ' generate 200 OK response')

    else:
        code = '404'
        phrase = 'Not Found'
        content_type = 'text/html'
        print('')
        print('--File ' + strroute + ' not found, generate response 404 Not Found response')

    return (code, phrase, content_type)

def is_method_post(method):
    if(method==b'POST'):
        return True
    else:
        return False

# return post request value as string
def parsePost(req):
    position = req.decode()
    position = position.split("\r\n\r\n")[-1]
    position = position[9:]
    position = position.strip('\n')
    return position

# ------------
# MAIN PROGRAM
# ------------
def main():
    board = ['', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    serverSocket, serverPort = InitializeServer()
    game_page, path, serverdirectory, error_page = openfile()
    # contains html page
    ren_page = game_page
    # initialize used spaces
    usedmoves = []
    while True:
        connectionSocket, addr = serverSocket.accept()
        req = connectionSocket.recv(4096)
        method, route, version = request_handler(req)
        code, phrase, content_type = generateResponseMessage(serverdirectory, method, route, path)
        print('requested method: ', method.decode() , ', Route: ', route)
        # initial html files
        if(method==b'GET'):
            ren_page=game_page

        # send error page
        if(code=='404') and (not(route==b'/favicon.ico')):
            ren_page = error_page

        # set to True on reset message
        reset = False
        if is_method_post(method):
            nwmove = parsePost(req)
            if(nwmove=='55'):
                reset = True
            #pass to application server if only move is valid and its not a reset POST
            if is_move_valid(nwmove) and (reset== False):
                clientmove = int(nwmove)
                generate_page, draw, playerwin, compwin = playgame(board, clientmove,ren_page)
                generate_page  = update_game_results(draw, playerwin, compwin, generate_page)
                ren_page = generate_page
            else:
                if(reset==False):
                    print('Illegal move from web client, discarded.')

        # reset server and game state
        if reset:
            board[:] = []
            board = ['', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
            #reset client state
            ren_page = game_page

        res = response_handler(version, code, phrase, content_type, ren_page)

        # send response message
        connectionSocket.send(res)
        connectionSocket.close()

if __name__ == '__main__':
    main()

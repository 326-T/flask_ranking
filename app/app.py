from flask import Flask,render_template,request
from app.tournament import Player, Swiss_System_Tournament, call_player, Log, Shuffle_Player

def make_match_format(match):
    shuffled = [shuffle_player.table.at[technique, match[0]], shuffle_player.table.at[technique, match[1]]]
    player = match
    url = ['/static/movie/' + technique + '/sub' + shuffled[0].split('選手')[-1] + '_' + technique + '.mp4', '/static/movie/' + technique + '/sub' + shuffled[1].split('選手')[-1] + '_' + technique + '.mp4']
    print(url)
    question = match[0] + 'と' + match[1] + 'ではどちらが上手ですか？'
    choice = [match[0] + 'の方が上手', 'どちらかといえば' + match[0] + 'の方が上手', 'どちらかといえば' + match[1] + 'の方が上手', match[1] + 'の方が上手']
    return player, url, question, choice

app = Flask(__name__)
log = Log()
swiss_tournament = Swiss_System_Tournament(11)
shuffle_player = Shuffle_Player(11)
technique = 'hoge'
username = 'huga'

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    global username
    username = str(request.form.get('username'))
    if len(username) > 0:
        return render_template("home.html", user=username)
    else:
        return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    return render_template("login.html")

@app.route("/technique", methods=["POST"])
def tech():
    global technique
    technique = str(request.form.get('technique'))
    log.Clear()
    swiss_tournament.Load('app/static/result/log/' + username + '_' + technique + '.csv')
    shuffle_player.Load('app/static/result/log/' + username + '.csv')
    log.Set_latest_match(swiss_tournament.Make_Match())
    player, url, question, choice = make_match_format(log.Get_next_match())
    if swiss_tournament.end:
        shuffle_player.Reverse_Save(swiss_tournament.vs_table, technique, 'app/static/result/' + username + '_' + technique + '_final.csv')
        return render_template("end.html")
    else:
        return render_template("ranking.html",player=player,url=url,question=question,choice=choice)

@app.route("/answer", methods=["POST"])
def ans():
    r = int(request.form.get('answer'))
    log.Report_match_result([r, -r])
    next_match = log.Get_next_match()
    if len(next_match) > 0 and (next_match[1] == "Bye"):
        log.Report_match_result([2,-2])
        next_match = log.Get_next_match()
        
    if len(next_match) == 0:
        swiss_tournament.Report_Match(log.latest_match, log.latest_result)
        swiss_tournament.Save('app/static/result/log/' + username + '_' + technique + '.csv')
        log.Save()
        if swiss_tournament.end:
            shuffle_player.Reverse_Save(swiss_tournament.vs_table, technique, 'app/static/result/' + username + '_' + technique + '_final.csv')
            return render_template("end.html")
        log.Set_latest_match(swiss_tournament.Make_Match())
        next_match = log.Get_next_match()
    
    player, url, question, choice = make_match_format(log.Get_next_match())
    return render_template("ranking.html",player=player,url=url,question=question,choice=choice)


@app.route("/back", methods=["POST"])
def back():
    if len(log.result_log) == 0 and len(log.latest_result) == 0:
        player, url, question, choice = make_match_format(log.Get_next_match())
        return render_template("ranking.html",player=player,url=url,question=question,choice=choice)
    else:
        if log.match_id == 0:
            swiss_tournament.Delete_Match(log.match_log[-1], log.result_log[-1])
            swiss_tournament.Save('app/static/result/log/' + username + '_' + technique + '.csv')

        log.Back()
        next_match = log.Get_next_match()
        if next_match[1] == "Bye":
            log.Back()
            next_match = log.Get_next_match()
        
        player, url, question, choice = make_match_format(log.Get_next_match())
        return render_template("ranking.html",player=player,url=url,question=question,choice=choice)

@app.route("/quit", methods=["POST"])
def quit():
    swiss_tournament.Save('app/static/result/log/' + username + '_' + technique +  '.csv')
    return render_template("home.html", user=username)

@app.route("/clear", methods=["POST"])
def clear():
    log.Clear()
    swiss_tournament.Load()
    log.Set_latest_match(swiss_tournament.Make_Match())
    player, url, question, choice = make_match_format(log.Get_next_match())
    return render_template("ranking.html",player=player,url=url,question=question,choice=choice)
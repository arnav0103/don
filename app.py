from Tool import app, db, socketio
from Tool.forms import RegistrationForm, LoginForm, MakeTeamForm, TeamLoginForm, MakeUpcoming, UpdateUserForm, UpdateTeamForm, Make_Rental, UpdateRent, KnowledgeForm, UpdateKnowledgeForm
from Tool.models import User, Team, Events, Rent, Knowledge
from flask import render_template, request, url_for, redirect, flash, abort
from flask_login import current_user, login_required, login_user, logout_user
from picture_handler import add_profile_pic, add_team_pic, add_rent_pic, add_knowledge_pic
import secrets
from sqlalchemy import desc, asc
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, abort
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

load_dotenv()
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_api_key_sid = os.environ.get('TWILIO_API_KEY_SID')
twilio_api_key_secret = os.environ.get('TWILIO_API_KEY_SECRET')
# imports


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.htm")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        user = User(name=form.name.data,
                    username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        if form.picture.data is not None:
            id = user.id
            pic = add_profile_pic(form.picture.data, id)
            user.profile_image = pic
            db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.htm', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = ''
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.check_password(form.password.data):

            login_user(user)
            flash('Log in Success!')

            next = request.args.get('next')
            if next == None or not next[0] == '/':
                next = url_for('index')
            return redirect(next)
        elif user is not None and user.check_password(form.password.data) == False:
            error = 'Wrong Password'
        elif user is None:
            error = 'No such login Pls create one'

    return render_template('login.htm', form=form, error=error)


@app.route('/maketeam', methods=['GET', 'POST'])
@login_required
def make_team():
    form = MakeTeamForm()

    if form.validate_on_submit():
        error = 'no'
        random = secrets.token_hex(8)
        randomid = random + form.team_name.data
        team = Team(name=form.team_name.data,
                    password=form.team_password.data,
                    randomid=randomid,
                    ownerid=current_user.id)
        db.session.add(team)
        current_user.teams.append(team)
        db.session.commit()

        return redirect(url_for('team', team_id=team.randomid))

        return redirect(url_for('join_team'))
    else:
        error = 'ono'
    return render_template('maketeam.htm', form=form, error=error)


@app.route('/jointeam', methods=['GET', 'POST'])
@login_required
def join_team():
    form = TeamLoginForm()
    if form.validate_on_submit():
        team = Team.query.filter_by(randomid=form.randomid.data).first()
        if team is not None and team.check_password(form.team_password.data):
            current_user.teams.append(team)
            db.session.commit()
            return redirect(url_for('team', team_id=team.randomid))

        elif team is not None and team.check_password(form.team_password.data) == False:
            error = 'Wrong Password'
        elif team is None:
            error = 'Wrong id .'
    return render_template('teamlogin.htm', form=form)
########## * ERROR HANDLERS * #############


@app.route('/<team_id>/<type>/makeupcoming', methods=['GET', 'POST'])
@login_required
def make_upcoming(team_id, type):
    error = ''
    print(type)
    team = Team.query.filter_by(randomid=team_id).first()
    form = MakeUpcoming()
    if form.validate_on_submit():
        if team is not None and team.ownerid == current_user.id:
            event = Events(teamid=team_id,
                           title=form.title.data,
                           event=form.description.data,
                           type=type)
            db.session.add(event)
            db.session.commit()
            return redirect(url_for('team', team_id=team_id))
        elif team is not None and team.ownerid != current_user.id:
            abort(403)
        elif team is None:
            error = 'No such team'
    return render_template('upcoming.htm', form=form, type=type)


@app.route('/<team_id>/team', methods=['GET', 'POST'])
@login_required
def team(team_id):
    team = Team.query.filter_by(randomid=team_id).first()
    if current_user in team.workers:
        team_upcoming = Events.query.filter_by(
            type='upcoming', teamid=team_id).order_by(Events.date.asc())
        team_ongoing = Events.query.filter_by(
            type='ongoing', teamid=team_id).order_by(Events.date.asc())
        team_completed = Events.query.filter_by(
            type='completed', teamid=team_id).order_by(Events.date.asc())
        team_owner = team.ownerid
    else:
        abort(403)
    return render_template('team.htm', team=team, team_owner=team_owner, team_upcoming=team_upcoming, team_ongoing=team_ongoing, team_completed=team_completed, team_id=team_id)


@app.route('/<team_id>/<event_id>/event', methods=['GET', 'POST'])
@login_required
def event(team_id, event_id):
    team = Team.query.filter_by(randomid=team_id).first()
    if current_user in team.workers:
        events = Events.query.filter_by(id=event_id).first()
    else:
        abort(403)
    return render_template('event.htm', events=events)


@app.route('/<team_id>/<event_id>/<type>/changeevent', methods=['GET', 'POST'])
@login_required
def change_event(team_id, event_id, type):
    team = Team.query.filter_by(randomid=team_id).first()
    event = Events.query.filter_by(id=event_id).first()
    if current_user in team.workers:
        if type == 'u':
            event.type = 'upcoming'
        elif type == 'o':
            event.type = 'ongoing'
        elif type == 'c':
            event.type = 'completed'
        db.session.commit()
    else:
        abort(403)
    return redirect(url_for('team', team_id=team_id))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    pic = current_user.profile_image
    form = UpdateUserForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data

        if form.picture.data is not None:
            id = current_user.id
            pic = add_profile_pic(form.picture.data, id)
            current_user.profile_image = pic

        flash('User Account Created')
        db.session.commit()
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename=current_user.profile_image)
    return render_template('account.htm', profile_image=profile_image, form=form, pic=pic)


@app.route('/<team_id>/teamaccount', methods=['GET', 'POST'])
@login_required
def team_account(team_id):
    team = Team.query.filter_by(randomid=team_id).first()
    if team is not None and current_user.id == team.ownerid:
        pic = team.team_image
        form = UpdateTeamForm()
        if form.validate_on_submit():
            team.randomid = form.randomid.data
            team.name = form.name.data

            if form.picture.data is not None:
                id = team.id
                pic = add_team_pic(form.picture.data, id)
                team.team_image = pic
                db.session.commit()
            flash('Team Account Created')
            db.session.commit()
            return redirect(url_for('team_account', team_id=team_id))
        elif request.method == 'GET':
            form.randomid.data = team.randomid
            form.name.data = team.name

        team_image = url_for('static', filename=team.team_image)
    else:
        abort(403)
    return render_template('account_team.htm', team_image=team_image, form=form, pic=pic, team=team)


@app.route('/allteams', methods=['GET', 'POST'])
@login_required
def all_teams():
    teams = []
    for team in current_user.teams:
        teams.append(team)
    return render_template('all_teams.htm', teams=teams)


@app.route('/makerental', methods=['GET', 'POST'])
@login_required
def make_rental():
    form = Make_Rental()
    if form.validate_on_submit():
        id = current_user.id
        pic = add_rent_pic(form.picture.data, id)
        rent = Rent(thing=form.thing.data,
                    description=form.description.data,
                    image=pic,
                    userid=id,
                    price=form.price.data)
        db.session.add(rent)
        db.session.commit()
        return redirect(url_for('all_rental'))
    return render_template('makerent.htm', form=form)


@app.route('/allrental', methods=['GET', 'POST'])
@login_required
def all_rental():
    rent = Rent.query.filter_by(rented='No').order_by(Rent.price.asc())
    return render_template('allrent.htm', rent=rent)


@app.route('/<rent_id>/single', methods=['GET', 'POST'])
@login_required
def single_rent(rent_id):
    rent = Rent.query.filter_by(id=rent_id).first()
    image = url_for('static', filename=rent.image)
    return render_template('single_rent.htm', rent=rent, image=image)


@app.route('/<rent_id>/update', methods=['GET', 'POST'])
@login_required
def update(rent_id):
    rent = Rent.query.filter_by(id=rent_id).first()
    form = UpdateRent()
    if rent is None:
        abort(404)
    elif current_user.id != rent.user.id:
        abort(403)
    else:
        pic = rent.image
        if form.validate_on_submit():
            rent.thing = form.thing.data
            rent.description = form.description.data
            rent.price = form.price.data
            rent.rented = form.rent.data
            if form.picture.data is not None:
                id = rent.id
                pic = add_rent_pic(form.picture.data, id)
                rent.image = pic
                db.session.commit()
            flash('Rent Account Updated')
            db.session.commit()
            return redirect(url_for('all_rental'))
        elif request.method == 'GET':
            form.thing.data = rent.thing
            form.description.data = rent.description
            form.price.data = rent.price
            form.rent.data = rent.rented

        image = url_for('static', filename=rent.image)
        return render_template('update.htm', image=image, rent=rent, form=form, rent_id=rent_id)


@app.route('/<rent_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(rent_id):
    rent = Rent.query.get_or_404(rent_id)
    if rent.user != current_user:
        abort(403)
    db.session.delete(rent)
    db.session.commit()
    flash('Rent deleted')
    return redirect(url_for('all_rental'))


@app.route('/yourrental', methods=['GET', 'POST'])
@login_required
def your_rental():
    rent = Rent.query.filter_by(
        userid=current_user.id).order_by(Rent.price.asc())
    return render_template('allrent.htm', rent=rent)


@app.route('/<team_id>/users', methods=['GET', 'POST'])
@login_required
def user_team(team_id):
    team = Team.query.filter_by(randomid=team_id).first()
    if current_user not in team.workers:
        abort(403)
    return render_template('user_team.htm', team=team)


@app.route('/<team_id>/knowledge', methods=['GET', 'POST'])
@login_required
def all_knowledge(team_id):
    team = Team.query.filter_by(randomid=team_id).first()
    image = []
    if team is None:
        abort(404)
    if current_user not in team.workers:
        abort(403)

    else:
        knowledge = Knowledge.query.filter_by(
            teamid=team_id).order_by(Knowledge.date.desc())
    return render_template('knowledge.htm', team_id=team_id, knowledge=knowledge)


@app.route('/<team_id>/makeknowledge', methods=['GET', 'POST'])
@login_required
def make_knowledge(team_id):
    team = Team.query.filter_by(randomid=team_id).first()
    if team is not None and current_user not in team.workers:
        abort(403)
    elif team is None:
        abort(404)
    else:
        form = KnowledgeForm()
        if form.validate_on_submit():
            knowledge = Knowledge(title=form.title.data,
                                  content=form.content.data,
                                  teamid=team_id,
                                  userid=current_user.id)

            db.session.add(knowledge)
            db.session.commit()

            if form.picture.data is not None:
                id = team.id
                pic = add_knowledge_pic(form.picture.data, id)
                knowledge.image = pic
                db.session.commit()
            return redirect(url_for('all_knowledge', team_id=team_id))
    return render_template('make_knowledge.htm', form=form)


@app.route('/<team_id>/<knowledge_id>/single_knowledge', methods=['GET', 'POST'])
@login_required
def single_knowledge(knowledge_id, team_id):
    team = Team.query.filter_by(randomid=team_id).first()
    if team is None:
        abort(404)
    elif current_user not in team.workers:
        abort(403)
    else:
        knowledge = Knowledge.query.get_or_404(knowledge_id)
    return render_template('single_knowledge.htm', knowledge=knowledge, team_id=team_id, team=team)


@app.route('/<team_id>/<knowledge_id>/update', methods=['GET', 'POST'])
@login_required
def update_knowledge(knowledge_id, team_id):
    knowledge = Knowledge.query.filter_by(id=knowledge_id).first()
    team = Team.query.filter_by(randomid=team_id).first()
    image = ''
    form = UpdateKnowledgeForm()
    if knowledge is None or team is None:
        abort(404)
    elif current_user.id != knowledge.user.id and current_user.id != team.ownerid:
        abort(403)
    else:
        pic = knowledge.image
        if form.validate_on_submit():
            knowledge.title = form.title.data
            knowledge.content = form.content.data
            if form.picture.data is not None:
                id = knowledge.id
                pic = add_knowledge_pic(form.picture.data, id)
                knowledge.image = pic
                db.session.commit()
            flash('Rent Account Updated')
            db.session.commit()
            return redirect(url_for('all_knowledge'))
        elif request.method == 'GET':
            form.title.data = knowledge.title
            form.content.data = knowledge.content
        if knowledge.image:
            image = url_for('static', filename=knowledge.image)
        return render_template('update_knowledge.htm', team_id=team_id, image=image, knowledge=knowledge, form=form, knowledge_id=knowledge_id)


@app.route('/<team_id>/<knowledge_id>/delete_k', methods=['GET', 'POST'])
@login_required
def delete_knowledge(team_id, knowledge_id):
    knowledge = Knowledge.query.get(knowledge_id)
    team = Team.query.filter_by(randomid=team_id).first()
    if knowledge is None or team is None:
        abort(404)
    elif current_user.id != knowledge.user.id and current_user.id != team.ownerid:
        abort(403)
    else:
        db.session.delete(knowledge)
        db.session.commit()
        flash('Knowledge deleted')
    return redirect(url_for('all_knowledge', team_id=team_id))


@app.route('/<event_id>/<team_id>/delete_event')
@login_required
def delete_event(event_id, team_id):
    event = Events.query.filter_by(id=event_id).first()
    team = Team.query.filter_by(randomid=team_id).first()
    if event is None:
        abort(404)
    elif current_user.id != team.ownerid:
        abort(403)
    else:
        db.session.delete(event)
        db.session.commit()
        return redirect(url_for('team', team_id=team_id))


@app.route('/vc')
def vc():
    return render_template('vc.html')


@app.route('/vc_login', methods=['POST'])
def vc_login():
    username = request.get_json(force=True).get('username')
    if not username:
        abort(401)

    token = AccessToken(twilio_account_sid, twilio_api_key_sid,
                        twilio_api_key_secret, identity=username)
    token.add_grant(VideoGrant(room='My Room'))

    return {'token': token.to_jwt().decode()}


@app.route('/<teamid>/chat', methods=['GET', 'POST'])
@login_required
def sessions(teamid):
    team = Team.query.filter_by(randomid=teamid).first()
    if team is None or current_user not in team.workers:
        abort(403)
    return render_template('chat.html')


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

###########################################


@app.errorhandler(404)
def page_not_found(e):
    return render_template('Error/404.html'), 404


@app.errorhandler(403)
def action_forbidden(e):
    return render_template('Error/403.html'), 403


@app.errorhandler(410)
def page_deleted(e):
    return render_template('Error/410.html'), 410


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('Error/500.html'), 500

##############################################


if __name__ == '__main__':
    socketio.run(app, debug=True)

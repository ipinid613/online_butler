from pymongo import MongoClient
import jwt
import datetime
import hashlib
import os

from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
from bson.objectid import ObjectId

from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/img"
app.config['SECRET_KEY'] = '123totallyrandommeaninglessstringsornums321'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

SECRET_KEY = 'SPARTA'

client = MongoClient('3.34.44.93', 27017, username="sparta", password="woowa")
db = client.hang31jo


# 메인
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        id_receive = request.form['id']
        pw_receive = request.form['pw']

        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        result = db.members.find_one({'id': id_receive, 'pw': pw_hash})

        if result is not None:
            payload = {
                'id': id_receive,
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
            }

            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

            return jsonify({'result': 'success', 'token': token, 'msg': '로그인 성공!'})
        else:
            return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 메인
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/get')
def getContents():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    contents = list(db.contents.find({}))
    for content in contents:
        content["_id"] = str(content["_id"])
        content["count_heart"] = db.like.count_documents({"_id": content["_id"]})
        content["heart_by_me"] = bool(db.like.find_one({"_id": content["_id"], "username": payload['id']}))
    return jsonify({'all_contents': contents})


@app.route('/lastes')
def lastes():
    lastes = list(db.contents.find({}, {'_id': False}).sort('uploadingTime', -1))
    return jsonify({'all_contents': lastes})


# 회원가입
@app.route('/sign_up')
def sign_up():
    msg = request.args.get("msg")
    return render_template('letin.html', msg=msg)


# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up_save():
    id_receive = request.form['id']
    pw_receive = request.form['pw']
    nickname_receive = request.form['nickname']
    password_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    doc = {
        "id": id_receive,  # 아이디
        "nickname": nickname_receive,  # 닉네임
        "pw": password_hash,  # 비밀번호
    }
    db.members.insert_one(doc)
    return jsonify({'result': 'success'})


# 중복가입체크 - 아이디
@app.route('/sign_up/checkDup', methods=['POST'])
def check_dup():
    id_receive = request.form['id']
    exists = bool(db.members.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 중복가입체크 - 닉네임
@app.route('/sign_up/nik_checkDup', methods=['POST'])
def nik_check_dup():
    nickname_receive = request.form['nickname']
    exists = bool(db.members.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 글쓰기
class PostingForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired()])
    content = StringField('내용', validators=[DataRequired()])
    img = FileField(validators=[DataRequired()])


class UpdatingForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired()])
    content = StringField('내용', validators=[DataRequired()])
    img = FileField()


@app.route('/contents', methods=['POST', 'GET'])
def upload():
    form = PostingForm()
    allowedExtensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    if form.validate_on_submit():
        token_receive = request.cookies.get('mytoken')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.members.find_one({'id': payload['id']}, {'_id': 0})
        nick = userinfo['nickname']
        filename = form.img.data.filename
        if '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in allowedExtensions:
            board = {
                "nick": nick,
                "subject": form.subject.data,
                "content": form.content.data,
                "imgPath": f'/static/img/{filename}',
                "uploadingTime": datetime.now(),
                "like": 0
            }

            db.contents.insert_one(board)
            form.img.data.save('./static/img/' + filename)
            target = db.points.find_one({'nickname': nick})
            if target:
                db.points.update_one(
                    {'nickname': nick},
                    {'$set': {'pts': target['pts'] + 5}}
                )
            else:
                db.points.insert_one({'nickname': nick, 'pts': 5})

            return redirect('/home')
    return render_template('write.html', form=form)


@app.route('/like', methods=['GET', 'POST'])
def like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.members.find_one({'id': payload['id']}, {'_id': 0})
        nick = userinfo['nickname']

        action = request.form['action_give']
        _id = request.form['_id_give']
        _id = ObjectId(_id)

        if action == "like":

            db.like.insert_one({'nickname': nick, '_id': _id})
        else:

            db.like.delete_one({'nickname': nick, '_id': _id})

        count = db.like.count_documents({'nickname': nick, '_id': _id})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect('/home')


_id = ''
@app.route('/a', methods=['GET','POST'])
def a():
    global _id
    _id = request.form['_id_give']
    _id = ObjectId(_id)
    return redirect(url_for('update'))

@app.route('/update', methods=['GET', 'POST'])
def update():
    form = UpdatingForm()
    allowedExtensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    target = db.contents.find_one({'_id': _id})
    subject = target['subject']
    content = target['content']
    del_path = target['imgPath'][1:]
    imgPath = '.' + target['imgPath']
    if request.method == 'POST':
        if form.img.data.filename:
            filename = form.img.data.filename
            if '.' in filename and \
                    filename.rsplit('.', 1)[1].lower() in allowedExtensions:
                db.contents.update_one(
                    {'_id': _id},
                    {'$set': {'subject': form.subject.data}}
                )
                db.contents.update_one(
                    {'_id': _id},
                    {'$set': {'content': form.content.data}}
                )
                db.contents.update_one(
                    {'_id': _id},
                    {'$set': {'imgPath': f'/static/img/{filename}'}}
                )
                form.img.data.save('./static/img/' + filename)
                os.remove(del_path)
                return redirect('/home')

        elif not form.img.data.filename:
            db.contents.update_one(
                {'_id': _id},
                {'$set': {'subject': form.subject.data}}
            )
            db.contents.update_one(
                {'_id': _id},
                {'$set': {'content': form.content.data}}
            )
            return redirect('/home')
    return render_template('update.html', form=form, subject=subject, content=content, imgPath=imgPath)

@app.route('/delete', methods=['POST','GET'])
def delete():
    _id = request.form['_id_give']
    del_Path = db.contents.find_one({'_id': ObjectId(_id)})['imgPath'][1:]
    os.remove(del_Path)
    db.contents.delete_one({'_id': ObjectId(_id)})
    return jsonify({'msg':'삭제되었습니다!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

csrf = CSRFProtect()
csrf.init_app(app)

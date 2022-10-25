import json
from settings import session
from tornado.web import RequestHandler
from models.UserModels import Users, UserGolds


class LoginHandler(RequestHandler):
    """
    用户登录
    """

    def get(self):
        pass

    def post(self):
        state, result = True, "登录成功"
        req_data = json.loads(self.request.body)
        username = req_data.get("username", "")
        password = req_data.get("password", "")
        if username and password:
            rememberme = req_data.get("rememberme", "off")
            if rememberme == 'on':
                self.set_secure_cookie("username", username)
                self.set_secure_cookie("password", password)
                self.set_secure_cookie("rememberme", "T")
            state, res = self.loginUser(username, password)
            if not state:
                result = res
            else:
                self.set_secure_cookie("currentuser", username)
        else:
            state = False
            result = "用户名或密码不能为空"
        self.finish({"status": state, "result": result})

    def loginUser(self, username, password):
        exists_username = session.query(Users).filter(Users.username == username).first()
        if not exists_username:
            return False, "不存在当前用户名"
        elif exists_username.auth_password(pwd=password):
            return True, "ok"
        else:
            return False, "密码错误"


class RegisterHandler(RequestHandler):
    """
    用户注册
    """

    def get(self):
        pass

    def post(self):
        result = "注册成功"
        req_data = json.loads(self.request.body)
        username = req_data.get("username", "")
        password = req_data.get("password", "")
        gender = req_data.get("gender", "1")
        if not username or not password:
            result = "注册失败，用户名或密码不能为空"
        state, res = self.createUser(username, password, gender)
        if not state:
            result = res
        self.finish({"result": result, "status": state})

    def createUser(self, username, password, gender):
        try:
            if session.query(Users.username == username).count():
                return False, 'Name is registered'
            user = Users()
            user.username = username
            user.password = password
            user.gender = gender
            session.add(user)
            session.commit()
            return True, "ok"
        except Exception as e:
            return False, e


class LogoutHandler(RequestHandler):
    """
    用户登出，设置cookie为None
    """

    def get(self):
        self.set_secure_cookie("currentuser", "")
        self.finish({"result": "登出成功。"})


class ForgetHandler(RequestHandler):
    """
    密码修改
    """

    def get(self):
        pass

    def post(self):
        status, result = True, "修改成功"
        req_data = json.loads(self.request.body)
        username = req_data.get("username", "")
        password_old = req_data.get("password_old", "")
        password_new = req_data.get("password_new", "")
        if not username or not password_new or not password_old:
            status, result = False, "用户名或密码不能为空"
        exists_username = session.query(Users).filter(Users.username == username).first()
        if exists_username and exists_username.auth_password(password_old):
            user = Users()
            user.password = password_new
            res = exists_username.update({"_password": user.password})
            # res = session.query(Users).filter_by(username = username).update({"_password": user.password})
            if 1 != res:
                result = "修改失败"
        else:
            result = "用户名或密码错误"
        self.finish({"status": status, "result": result})
